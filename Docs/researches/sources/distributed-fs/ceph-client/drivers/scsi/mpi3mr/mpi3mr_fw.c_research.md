# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_fw.c

## Purpose

`mpi3mr_fw.c` is the firmware-facing controller management layer for the Broadcom MPI3 SCSI low-level driver. It owns PCI BAR setup, MSI-X interrupt setup, admin and operational queue registration, IOC facts/init/port-enable handshakes, firmware event subscription, persistent event log wait handling, controller fault detection, reset/reinit orchestration, DMA buffer lifetime, and generic MPI3 configuration page accessors.

The file sits between OS-facing code in `mpi3mr_os.c`/`mpi3mr_transport.c`/`mpi3mr_app.c` and the MPI3 firmware ABI declared by the `mpi/mpi30_*.h` headers. Its central object is `struct mpi3mr_ioc`, whose register mapping, DMA queues, reply pools, command trackers, event masks, reset flags, watchdog work, diagnostic buffers, PEL state, and SAS transport state are populated and mutated here.

## Important APIs, Types, and Functions

The main exported entry points are:

- `mpi3mr_setup_resources()` and `mpi3mr_cleanup_resources()`: enable/disable PCI memory resources, map/unmap system interface registers, select BARs, set DMA mask, discover MSI-X vector count, and store `Scsi_Host` driver data.
- `mpi3mr_init_ioc()` and `mpi3mr_reinit_ioc()`: perform first-time and reset/resume controller initialization. They bring the IOC to ready, issue IOC facts/init, allocate reply/sense/chain/PEL/throttle resources, post diagnostic buffers, create operational queues, enable events, refresh triggers, and initiate port enable on reinit.
- `mpi3mr_cleanup_ioc()` and `mpi3mr_free_mem()`: quiesce firmware with MUR/shutdown when possible, then free all DMA pools, queue segments, command reply buffers, bitmaps, diagnostic buffers, throttle groups, and log buffers.
- `mpi3mr_admin_request_post()` and `mpi3mr_op_request_post()`: post MPI3 requests to admin or operational producer rings, update producer indexes in MMIO, and enforce reset/unrecoverable/PCI-error gating.
- `mpi3mr_process_admin_reply_q()` and `mpi3mr_process_op_reply_q()`: drain reply descriptor queues from ISR, threaded IRQ polling, or blk-mq poll paths. They track phase bits, consumer indexes, request queue CIs, reply buffer reposting, and in-use serialization.
- `mpi3mr_blk_mq_poll()`: blk-mq polling hook that drains a selected operational reply queue when the controller is not resetting or unrecoverable.
- `mpi3mr_soft_reset_handler()`: blocking reset coordinator. It serializes reset attempts, blocks SCSI requests, optionally captures snapdump, resets firmware, drains queue processors, flushes internal and host I/O state, reinitializes the IOC, restarts PEL/watchdog flow, or marks the controller unrecoverable.
- `mpi3mr_start_watchdog()` and `mpi3mr_stop_watchdog()`: manage the ordered workqueue that monitors faults, reset history, timestamp sync, invalid completions, prepare-for-reset timeout, and controller disappearance.
- `mpi3mr_process_event_ack()`: sends synchronous event acknowledgements through the admin queue.
- `mpi3mr_pel_get_seqnum_post()` plus internal PEL callbacks: maintain persistent event log wait/retry sequence and signal applications through `event_counter`.
- `mpi3mr_cfg_get_*()` and `mpi3mr_cfg_set_sas_io_unit_pg1()`: synchronous config-page helpers for device, SAS phy, expander, enclosure, SAS IO unit, and driver pages.

Important supporting types come from `mpi3mr.h`: `struct mpi3mr_ioc` is the adapter anchor; `struct mpi3mr_drv_cmd` tracks internal admin/config/BSG/TM/PEL commands; `struct op_req_qinfo` and `struct op_reply_qinfo` describe operational request/reply rings and segment lists; `struct mpi3mr_intr_info` binds MSI-X vectors to reply queues. The firmware request/reply and config structures are MPI3 ABI types from the `mpi30_*` headers.

## Control Flow

Initial probe normally enters through `mpi3mr_setup_resources()` from OS code, then `mpi3mr_init_ioc()`. Initialization first calls `mpi3mr_bring_ioc_ready()`, which reads IOC status/config/info registers, handles fault/reset states, may issue MUR or soft reset, allocates/registers the admin queue pair, sets `ENABLE_IOC`, and waits for `MRIOC_STATE_READY`. A single interrupt vector is installed so admin commands can complete. `mpi3mr_issue_iocfacts()` then retrieves firmware limits; `mpi3mr_process_factsdata()` converts endianness and caches queue, DMA, firmware, topology, throttle, diagnostic, and capability fields into `mrioc->facts`. The driver allocates diagnostic, ioctl, reply, sense, and chain buffers, issues `MPI3_FUNCTION_IOC_INIT`, prints package/version data, installs the full interrupt layout, creates operational request/reply queue pairs, enables selected firmware events, and refreshes diagnostic trigger configuration.

Admin commands use `struct mpi3mr_drv_cmd` instances keyed by reserved host tags. `mpi3mr_admin_request_post()` copies a request into the admin request ring, advances `admin_req_pi`, and writes the producer index. `mpi3mr_process_admin_reply_q()` drains descriptors while the phase bit matches, decodes status/address/success replies in `mpi3mr_process_admin_reply_desc()`, maps the host tag to an internal command, copies replies and sense data when present, completes waiters or invokes callbacks, reposts reply buffers, and writes the admin reply consumer index.

Operational I/O requests are posted by `mpi3mr_op_request_post()` into segmented or contiguous request rings. It checks queue-full state, opportunistically drains the paired reply queue, rejects submissions during reset or PCI error recovery, optionally throttles when reply queues near a firmware-reported limit, copies the request, increments pending I/O count, may request threaded IRQ polling, and rings the producer index. Operational completions flow through `mpi3mr_process_op_reply_q()`, which drains phase-matching descriptors, updates request queue CIs, delegates descriptor-specific SCSI completion work to `mpi3mr_process_op_reply_desc()` in OS code, reposts reply buffers, and periodically writes consumer indexes to limit MMIO churn.

Interrupt setup allocates one or more MSI-X vectors with optional affinity and optional io_uring poll queues. Vector 0 services admin replies; operational reply queues are bound to vectors using `op_reply_q_offset`. On non-RT kernels, `mpi3mr_isr()` can wake a threaded polling handler when a queue has many pending completions; `mpi3mr_isr_poll()` drains until pending I/O falls away or a max-I/O budget is reached.

Fault and reset control is split across the watchdog and explicit reset entry points. `mpi3mr_watchdog_work()` runs every second, emits uevents for initialization faults, flushes commands if the device becomes unrecoverable, syncs timestamps, handles reset-history and fault bits, captures diagnostic trigger data, and invokes `mpi3mr_soft_reset_handler()` when recovery is possible. The soft reset handler blocks new SCSI requests and BSGs, masks/release diagnostics when appropriate, waits for host I/O, disables interrupts, issues a soft reset or snapdump fault-reset plus soft reset, waits for reply-queue processors to quiesce, flushes internal command trackers and OS/device lists, clears bitmaps and buffers, releases diagnostics, reinitializes the IOC, waits for topology settle, unblocks SCSI, and reposts PEL wait if enabled.

Config helpers use a two-step pattern: first read the page header, then allocate coherent DMA for the page, set a simple end-of-list SGE, post `MPI3_FUNCTION_CONFIG`, and copy data in or out based on read/write action. Page attributes are checked so read-only and changeable pages are not written with invalid actions.

## State and Persistence Behavior

Most state is volatile kernel memory attached to `struct mpi3mr_ioc`: queue indices, phase bits, MSI-X bindings, command states, reply and sense DMA pools, event masks, firmware facts, diagnostic trigger state, fault counters, PEL sequence numbers, and reset flags. Firmware-visible state is exchanged through MMIO registers, DMA queues, IOC init data, event masks, config pages, diagnostic buffers, and shutdown/reset commands.

Persistent firmware configuration can be modified by `mpi3mr_cfg_set_sas_io_unit_pg1()`, which writes both current and persistent SAS IO Unit page 1. Driver page reads can affect runtime timestamp-update interval and diagnostic trigger behavior. The file also records fault metadata in `saved_fault_code`/`saved_fault_info` and emits it through a uevent, but it does not persist that data to disk.

Queue memory is deliberately reused across resets when possible. `mpi3mr_memset_buffers()` clears existing DMA and tracker state so `mpi3mr_reinit_ioc()` can recreate firmware queue registrations without reallocating everything. `mpi3mr_free_mem()` is the terminal teardown path and must remain synchronized with all allocation paths in init, ioctl DMA setup, diagnostic posting, segmented trace buffers, and queue segment creation.

## Dependencies and Integration Points

This file depends on Linux PCI, DMA pool/coherent allocation, MSI-X IRQ APIs, blk-mq polling, SCSI host request blocking, workqueues, completions, mutexes, spinlocks, atomics, bitmaps, kobject uevents, jiffies/time APIs, and endian conversion helpers. It directly accesses MPI3 system interface registers through `mrioc->sysif_regs` with `readl()`, `writel()`, and a 64-bit write helper that falls back to locked two-register writes on platforms without native `writeq()`.

Driver-local integration points include:

- `mpi3mr_os.c`: probe/remove/suspend/resume/error-recovery call the setup/init/reinit/cleanup APIs; SCSI I/O posting uses `mpi3mr_op_request_post()`; SCSI completion handling is delegated to `mpi3mr_process_op_reply_desc()`; event processing is delegated to `mpi3mr_os_handle_events()`.
- `mpi3mr_transport.c`: SAS topology refresh and transport management call config-page helpers and admin-posting helpers.
- `mpi3mr_app.c`: BSG/ioctl, diagnostic buffer management, PEL controls, and app-triggered resets share admin posting, config helpers, PEL state, and reset handling.
- `mpi3mr_debug.h` and app diagnostic code: reply/event/sense/diagnostic trigger helpers such as `mpi3mr_reply_trigger()`, `mpi3mr_scsisense_trigger()`, `mpi3mr_set_trigger_data_in_all_hdb()`, `mpi3mr_post_diag_bufs()`, and `mpi3mr_release_diag_bufs()` are invoked during completions and recovery.

## Risks and Edge Cases

The highest-risk areas are reset and concurrent queue processing. Admin and operational reply queues use atomic `in_use` guards, pending ISR counters, phase bits, and MMIO consumer updates; races here can lose completions, double-complete internal commands, leave pending I/O counts wrong, or force the controller unrecoverable after `mpi3mr_check_op_admin_proc()` times out. Reset paths also coordinate with SCSI request blocking, BSG blocking, diagnostic buffer release, PEL callbacks, watchdog requeueing, and host I/O flushing.

DMA lifetime is another sensitive area. Reply buffers, sense buffers, admin queues, segmented operational queues, ioctl SGEs, chain buffers, PEL sequence memory, diagnostic buffers, and trace buffer segments have different allocation/free paths. Partial allocation failures often return `-1` after helper-level cleanup, so teardown must tolerate partially initialized structures. `mpi3mr_alloc_op_*_segments()` can fail after allocating earlier segments; callers rely on the paired free helper to walk existing segment arrays.

Queue sizing is firmware-dependent. IOC facts must not shrink reply size, operational queue counts, or runtime limits during reset; `mpi3mr_revalidate_factsdata()` rejects incompatible changes but only warns for max transfer size changes that the SCSI host cannot alter live. Incorrect facts conversion or DMA mask changes can break queue registration or data DMA.

Event and PEL handling are callback-driven. A stale command state, missing reply copy, aborted PEL wait, or reset-completed command can disable PEL or fail to notify applications. Event notification uses an inverted mask bitmap; wrong unmasking can either miss topology/fault events or overload the OS event worker.

The config-page processor enforces page attributes but still trusts caller-supplied `pg_sz` and page-address forms. Callers that ignore returned `ioc_status` where documented can treat a firmware-level failure as valid empty data. Persistent SAS IO Unit writes are especially risky because they alter firmware configuration beyond the current boot session.

## Test Signals

Useful build-level signals are successful compilation of the `mpi3mr` driver with `CONFIG_SCSI_MPI3MR`, including both normal and `CONFIG_PREEMPT_RT` IRQ code paths, plus sparse/endian checks around MPI3 little-endian fields.

Runtime probe signals include PCI resource setup logs, correct MSI-X vector allocation, IOC facts logs matching firmware limits, successful IOC init, firmware package version print, operational queue creation counts, event-notification success, and port-enable completion. I/O path signals include successful SCSI discovery and I/O under interrupt mode, blk-mq poll mode with `poll_queues`, queue-full recovery counters, no stuck `pend_ios`, and balanced reply/sense buffer reposting.

Recovery tests should cover firmware reset-history, recoverable fault, unrecoverable fault, snapdump-triggered reset, invalid I/O completion, admin command timeout, config request timeout, port-enable timeout, PCI error recovery, suspend/resume reinit, and kdump/reduced-resource initialization. Expected signals are SCSI request blocking/unblocking, internal command completions with `MPI3MR_CMD_RESET`, diagnostic trigger updates, uevents with saved fault data, successful `mpi3mr_reinit_ioc()`, restored operational queue count, and no leaked workqueue or IRQ state.

Config and topology tests should exercise device, SAS phy, expander, enclosure, SAS IO Unit, and driver page reads, including non-success `ioc_status` paths. Persistent SAS IO Unit page writes require explicit validation that both current and persistent actions succeed and that invalid page attributes are rejected.
