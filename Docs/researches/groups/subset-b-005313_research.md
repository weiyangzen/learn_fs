# Research Report: subset-b-005313

Work item `subset-b-005313` covers the mpt3sas management, debug, and debugfs support files under `sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.c -->
# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.c

## Purpose

`mpt3sas_ctl.c` implements the mpt3sas/mpt2sas management control plane. It registers the `/dev/mpt3ctl` and `/dev/mpt2ctl` misc devices, dispatches user-space ioctls, exposes SCSI host/device sysfs attributes, handles event notification for poll/fasync users, manages host diagnostic buffers, and exports an in-kernel MCTP passthrough API. It is not normal SCSI data-path code; it is a privileged management interface that can post raw MPI requests, trigger resets, read adapter state, and alter diagnostic/queueing behavior.

## Important APIs, Types, And Entry Points

- Misc-device entry points: `_ctl_ioctl()`, `_ctl_mpt2_ioctl()`, compat variants, `_ctl_poll()`, and `_ctl_fasync()` are wired through `ctl_fops` and `ctl_gen2_fops`.
- Main ioctl dispatcher: `_ctl_ioctl_main()` copies `struct mpt3_ioctl_header`, resolves an adapter with `_ctl_verify_adapter()`, serializes against `ioc->pci_access_mutex` and `ioc->ctl_cmds.mutex`, gates recovery/removal states, then dispatches `MPT3IOCINFO`, `MPT3COMMAND`, event ioctls, diagnostic ioctls, hard reset, BTDH mapping, and SBR reload.
- Firmware passthrough: `_ctl_do_mpt_command()` copies a user MPI frame, allocates coherent DMA buffers, builds SGL/PRP entries, submits by request function, waits for completion, copies replies/data/sense back, and may trigger target or host reset on timeout/error paths.
- Completion/event callbacks: `mpt3sas_ctl_done()` completes pending control commands and captures reply, SCSI sense, or NVMe error-response data. `mpt3sas_ctl_event_callback()` and `mpt3sas_ctl_add_to_event_log()` maintain the ioctl event ring and notify poll/fasync waiters.
- Diagnostic buffer lifecycle: `_ctl_diag_register_2()`, `_ctl_diag_register()`, `_ctl_diag_unregister()`, `_ctl_diag_query()`, `mpt3sas_send_diag_release()`, `_ctl_diag_release()`, `_ctl_diag_read_buffer()`, `_ctl_addnl_diag_query()`, `mpt3sas_enable_diag_buffer()`, and `_ctl_enable_diag_sbr_reload()` manage trace/snapshot/extended buffers posted to firmware.
- BTDH mapping helpers: `_ctl_btdh_search_sas_device()`, `_ctl_btdh_search_pcie_device()`, `_ctl_btdh_search_raid_device()`, and `_ctl_btdh_mapping()` translate bus/id to firmware handle and back.
- MCTP exported API: `mpt3sas_get_device_count()` and `mpt3sas_send_mctp_passthru_req()` are exported symbols for other kernel code needing MCTP passthrough through capable HBAs.
- Lifecycle: `mpt3sas_ctl_init()`, `mpt3sas_ctl_release()`, and `mpt3sas_ctl_exit()` register/deregister control devices and free per-adapter diagnostic/event allocations.
- Sysfs groups: `mpt3sas_host_groups` and `mpt3sas_dev_groups` collect read/write attributes for firmware versions, board identity, debug knobs, trace buffers, diagnostic triggers, queue-depth behavior, SAS identity, and SATA NCQ priority.

## Control Flow

The ioctl path begins in `_ctl_ioctl()` or `_ctl_mpt2_ioctl()`, which select the accepted MPI generation and call `_ctl_ioctl_main()`. The dispatcher reads the common header from user memory, looks up the IOC in `mpt3sas_ioc_list` under `gioc_lock`, locks PCI access, rejects operations while recovery/loading/removal is active, and then takes `ioc->ctl_cmds.mutex`. Nonblocking opens use `mutex_trylock()` and return `-EAGAIN` if another control command is in flight; blocking callers can sleep interruptibly.

For `MPT3COMMAND`, `_ctl_do_mpt_command()` verifies the SGE offset cannot overflow the request frame, copies the user MPI request prefix, selects an SMID, marks `ioc->ctl_cmds` pending, copies the request into the firmware frame, allocates coherent buffers for inbound/outbound data, then dispatches by `Function`. SCSI, RAID, SATA, NVMe, task-management, SMP, firmware upload/download, toolbox, SAS IO unit control, and MCTP all have specialized setup for sense buffers, device removal checks, task-mid matching, PRP/SGL construction, link-reset flags, and ATTO firmware-download rejection. After submission it waits at least `MPT3_IOCTL_DEFAULT_TIMEOUT` seconds. Completion is observed through `mpt3sas_ctl_done()`, which copies the reply and wakes the completion. Timeout calls `mpt3sas_check_cmd_timeout()` and can escalate to target reset or `mpt3sas_base_hard_reset_handler()`.

Diagnostic buffer registration follows a similar command-submission path but uses `MPI2_FUNCTION_DIAG_BUFFER_POST`. `_ctl_diag_register_2()` validates IOC state, capability, unique id, ownership, release state, and 4-byte alignment; allocates or reuses coherent diagnostic memory; records product-specific and diagnostic flags; posts the buffer; and marks `MPT3_DIAG_BUFFER_IS_REGISTERED` on success. Release sends `MPI2_FUNCTION_DIAG_RELEASE`; read copies a bounded segment to user memory and can optionally repost if `MPT3_FLAGS_REREGISTER` is set.

Event flow is interrupt-driven. Firmware event replies reach `mpt3sas_ctl_event_callback()`, which stores matching events in `ioc->event_log` based on `ioc->event_type[]`. `mpt3sas_ctl_add_to_event_log()` writes a circular entry, increments `event_context`, sets `aen_event_read_flag`, wakes `ctl_poll_wait`, and sends SIGIO through `async_queue`. `MPT3EVENTREPORT` copies the ring to user memory and clears the read flag.

Sysfs flow is mostly direct reads from `struct MPT3SAS_ADAPTER`, with selected write paths changing live state. `logging_level_store()` and `fwfault_debug_store()` update debug fields. `host_trace_buffer_enable_store()` posts or releases the trace buffer. Diagnostic trigger stores optionally update firmware driver-trigger pages and then update in-memory trigger structures under `diag_trigger_lock`. `enable_sdev_max_qd_store()` walks all SCSI devices and changes queue depths based on the requested mode and target type.

## State And Persistence Behavior

State is in kernel memory and adapter firmware, not on disk. Persistent or externally visible state includes:

- Global control state: `async_queue` and `ctl_poll_wait` support notification for all control-device users.
- Per-adapter command state: `ioc->ctl_cmds.status`, `smid`, `reply`, `sense`, `done`, and `mutex` serialize exactly one control command per IOC.
- Event state: `ioc->event_type[]`, `ioc->event_log`, `ioc->event_context`, and `ioc->aen_event_read_flag` persist until adapter release.
- Diagnostic state: `ioc->diag_buffer[]`, DMA addresses/sizes, `diag_buffer_status[]`, `unique_id[]`, `product_specific[][]`, `diagnostic_flags[]`, `htb_rel`, ring-buffer size/offset, and trigger structures track ownership, release, driver allocation, reset release, and firmware-post status.
- Reset state: pre-reset releases registered diagnostic buffers, clear-outstanding marks pending ioctls with `MPT3_CMD_RESET`, and reset-done marks unreleased registered buffers as reset-released.
- Sysfs writes are live in-memory changes. Some diagnostic trigger writes also update firmware configuration pages when `ioc->supports_trigger_pages` is true. Firmware/BIOS/NVDATA version attributes are derived from already-read config pages/facts.
- Misc-device registration is process-global during driver lifetime and depends on `hbas_to_enumerate`: the code can skip either gen2 or gen3 control device.

## Dependencies And Integration Points

The file depends heavily on `mpt3sas_base.h` and the wider mpt3sas driver: adapter lists and locks, SMID allocation/freeing, reply/sense lookup, request posting callbacks, SGL/PRP builders, reset handling, IOC state/facts, device lists, config-page helpers, target/device lookup, queue-depth changes, and diagnostic trigger page updates. Kernel dependencies include misc devices, uaccess, DMA coherent allocation, completions, mutexes/spinlocks, wait queues, poll/fasync, sysfs attribute groups, SCSI host/device APIs, PCI state, and ATA NCQ priority helpers. User-space ABI structures and ioctl numbers are defined in `mpt3sas_ctl.h`.

The exported MCTP functions integrate with other kernel modules without going through `copy_from_user()`. They still reuse `ioc->ctl_cmds`, the reserved passthrough SMID, DMA buffers, and the MCTP request-building helper, so they share serialization and timeout behavior with ioctl passthrough.

## Risks And Edge Cases

- This file exposes a high-privilege raw firmware passthrough ABI. Bugs in validation, request sizing, SGL construction, or reset escalation can affect devices behind the HBA or the host.
- `ioc->ctl_cmds.status` is checked outside and inside mutex-protected paths in different helpers; correctness relies on the dispatcher/exported API taking `ctl_cmds.mutex` and on reset callbacks completing pending commands.
- Several paths allocate coherent DMA buffers sized by user-provided fields. Basic offset/wrap validation exists for request SGE offset and diagnostic read ranges, but stress around very large transfer sizes, allocation failure, and timeout cleanup is important.
- Event-log fields are updated from interrupt context and read/reset from ioctl context with limited explicit locking, so tests should focus on race tolerance and memory lifetime during adapter removal.
- Diagnostic buffer ownership is complex: driver-allocated vs app-owned, registered vs released, reset-released, and unique-id matching. Regression risk is high around app re-register, sysfs trace-buffer enable, and unload cleanup.
- `host_trace_buffer_store()` accepts signed decimal offset and assigns it to `ioc->ring_buffer_offset`; negative input behavior depends on the field type and should be considered in validation/review.
- `enable_sdev_max_qd_store()` assumes target/raid-device relationships are valid while iterating SCSI devices; null checks are partial, so hotplug/removal races are relevant.
- Debug/diagnostic sysfs attributes can return binary structures through sysfs show functions for trigger data; callers must know the exact structure size and layout.
- The MCTP exported path uses `GFP_ATOMIC` coherent allocation while holding mutexes and copies kernel buffers directly; callers must provide valid kernel pointers and tolerate `-EAGAIN`/timeout/reset behavior.

## Test Signals

Useful validation signals include successful registration of `/dev/mpt3ctl` and `/dev/mpt2ctl`, ioctl ABI smoke tests for `MPT3IOCINFO`, event enable/query/report, BTDH mapping with SAS/PCIe/RAID devices, and negative tests for wrong IOC number, wrong ioctl size, wrong generation device, nonblocking busy behavior, recovery/removal state, invalid device handles, invalid diagnostic unique ids, and unaligned diagnostic reads. Passthrough tests should cover SCSI, SATA, SMP, NVMe, toolbox, firmware upload/download rejection on ATTO HBAs, and MCTP capability gating. Fault injection should exercise DMA allocation failures, user copy failures, firmware timeout, task-management timeout/reset, diagnostic repost after release, and adapter reset during pending ioctl. Sysfs tests should verify all host/device attributes exist, read expected values, reject invalid stores, update `logging_level`, `fwfault_debug`, NCQ priority, trace-buffer post/release/read offset, diagnostic triggers, and queue-depth behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.h -->
# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.h

## Purpose

`mpt3sas_ctl.h` defines the user-visible and in-kernel management ABI for the mpt3sas control module. It provides misc-device names/minors, ioctl numbers, ioctl payload layouts, diagnostic-buffer flags, event-log payload formats, MCTP passthrough command structure, and exported function prototypes. This header is the contract consumed by `mpt3sas_ctl.c` and by user-space management tools that issue `/dev/mpt3ctl` or `/dev/mpt2ctl` ioctls.

## Important APIs, Types, And Constants

- Device identity: `MPT2SAS_DEV_NAME`, `MPT3SAS_DEV_NAME`, `MPT2SAS_MINOR`, and `MPT3SAS_MINOR` identify the gen2/gen3 misc devices.
- Ioctl opcodes: `MPT3IOCINFO`, `MPT3COMMAND`, compat `MPT3COMMAND32`, event ioctls, `MPT3HARDRESET`, `MPT3BTDHMAPPING`, diagnostic register/release/unregister/query/read/additional-query, and `MPT3ENABLEDIAGSBRRELOAD`.
- Common header: `struct mpt3_ioctl_header` carries `ioc_number`, `port_number`, and `max_data_size` and prefixes every ioctl payload.
- Controller info: `struct mpt3_ioctl_iocinfo` returns adapter type, PCI ids, firmware/BIOS/driver versions, SCSI id, capability bits, and packed PCI topology in `struct mpt3_ioctl_pci_info`.
- Event ABI: `MPT3SAS_CTL_EVENT_LOG_SIZE`, `MPT3_EVENT_DATA_SIZE`, `struct MPT3_IOCTL_EVENTS`, query/enable/report payloads define a fixed-size circular event snapshot interface.
- Firmware passthrough: `struct mpt3_ioctl_command` contains user pointers for reply, data in/out, sense data, sizes, timeout, SGE offset, and a flexible message-frame tail. `struct mpt3_ioctl_command32` maps the same ABI for 32-bit compat pointers.
- BTDH mapping: `struct mpt3_ioctl_btdh_mapping` supports bus/id-to-handle and handle-to-bus/id lookup using sentinel values.
- Diagnostic buffers: `MPT3_APP_FLAGS_*`, `MPT3_FLAGS_REREGISTER`, `MPT3_PRODUCT_SPECIFIC_DWORDS`, and `struct mpt3_diag_*` payloads define register, unregister, query, release, read, additional release-query, and SBR reload commands.
- MCTP in-kernel API: `struct mpt3_passthru_command`, `mpt3sas_get_device_count()`, and `mpt3sas_send_mctp_passthru_req()` expose a kernel-callable passthrough interface.

## Control Flow And Usage

All ioctl payloads begin with `struct mpt3_ioctl_header`; `mpt3sas_ctl.c` reads this header before dispatch so it can resolve the IOC and validate command size. For generic passthrough, user space fills `struct mpt3_ioctl_command`, points its buffer fields at user memory, sets transfer sizes and `data_sge_offset`, and appends the MPI request frame in `mf[1]`. The driver copies the request prefix up to the SGE offset, supplies DMA-backed SGLs/PRPs, waits for firmware completion, then copies data/reply/sense back through the provided pointers.

Diagnostic commands use unique ids to claim or find buffers. Register supplies buffer type, flags, product-specific dwords, requested size, and unique id. Query can use either buffer type or unique id. Release gives firmware ownership back to the driver/application boundary, read copies data starting at an aligned offset and can request repost via `MPT3_FLAGS_REREGISTER`, and unregister frees or returns the buffer depending on whether it was driver allocated.

The MCTP kernel API bypasses user pointers: `struct mpt3_passthru_command` holds kernel buffer pointers plus an `Mpi26MctpPassthroughRequest_t *`, and the implementation selects the HBA by `dev_index` among MCTP-capable adapters.

## State And Persistence Behavior

The header itself stores no state, but its layouts define the durable ABI between user-space tools and the kernel driver. Field sizes, ioctl numbers, and pointer layout are ABI-sensitive. `MPT2DIAGBUFFUNIQUEID`, `MPT3DIAGBUFFUNIQUEID`, and `MPT3_DIAG_UID_NOT_FOUND` are semantic values persisted in in-memory adapter diagnostic state and used across register/query/release/unregister operations. Event-log sizes and diagnostic product-specific array lengths constrain the driver's per-adapter allocations and copy sizes.

## Dependencies And Integration Points

The header includes `mpt3sas_base.h` for MPI types such as `Mpi26MctpPassthroughRequest_t` and `struct htb_rel_query`. Under `__KERNEL__` it includes `<linux/miscdevice.h>`. User-space compatibility depends on stable Linux ioctl encoding and exact structure packing for native and compat command layouts. The command structures integrate with `copy_from_user()`, `copy_to_user()`, DMA setup, sysfs diagnostic triggers, and MCTP-capable firmware paths in `mpt3sas_ctl.c`.

## Risks And Edge Cases

- ABI drift is the main risk. Reordering fields, changing widths, or changing ioctl numbers would break existing management utilities.
- `struct mpt3_ioctl_command` contains raw user pointers and a one-byte flexible tail pattern. The implementation must validate sizes and copy bounds carefully.
- Compat support only covers pointer conversion for the generic command; other payloads rely on identical native/compat layout.
- Event enable uses `event_types[4]`, while query uses `MPI2_EVENT_NOTIFY_EVENTMASK_WORDS`; these must remain consistent with the firmware event mask width expected by the implementation.
- Diagnostic unique ids are user/app selected except for default driver ids, so duplicate or zero ids must be rejected in implementation.
- `struct mpt3_passthru_command` is kernel-only but still has caller-provided pointers and sizes; misuse by another module can trigger invalid memory access or firmware failures.

## Test Signals

Compile-time signals include successful builds with and without `CONFIG_COMPAT`, correct ioctl size checks in the implementation, and no sparse/checkpatch warnings for user pointers. ABI tests should verify native and 32-bit compat `MPT3COMMAND`, all diagnostic payload sizes, event log sizing, and BTDH sentinel behavior. Integration tests should confirm `MPT3IOCINFO.driver_capability` reports MCTP passthrough consistently with the exported MCTP capability and that user tools built against this header interoperate with the control device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debug.h -->
# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debug.h

## Purpose

`mpt3sas_debug.h` centralizes logging bit definitions, conditional debug-print macros, and inline frame-dump helpers for the mpt3sas driver. It lets other mpt3sas files guard expensive or noisy diagnostics behind `ioc->logging_level` bits and provides standard dumps for MPI message frames, replies, and config pages.

## Important APIs, Types, And Macros

- Logging bits: `MPT_DEBUG`, `MPT_DEBUG_MSG_FRAME`, `MPT_DEBUG_SG`, `MPT_DEBUG_EVENTS`, `MPT_DEBUG_EVENT_WORK_TASK`, `MPT_DEBUG_INIT`, `MPT_DEBUG_EXIT`, `MPT_DEBUG_FAIL`, `MPT_DEBUG_TM`, `MPT_DEBUG_REPLY`, `MPT_DEBUG_HANDSHAKE`, `MPT_DEBUG_CONFIG`, `MPT_DEBUG_DL`, `MPT_DEBUG_RESET`, `MPT_DEBUG_SCSI`, `MPT_DEBUG_IOCTL`, `MPT_DEBUG_SAS`, `MPT_DEBUG_TRANSPORT`, `MPT_DEBUG_TASK_SET_FULL`, and `MPT_DEBUG_TRIGGER_DIAG`.
- Conditional macro core: `MPT_CHECK_LOGGING(IOC, CMD, BITS)` executes `CMD` only when `IOC->logging_level` contains the requested bit.
- Convenience wrappers: `dprintk`, `dsgprintk`, `devtprintk`, `dewtprintk`, `dinitprintk`, `dexitprintk`, `dfailprintk`, `dtmprintk`, `dreplyprintk`, `dhsprintk`, `dcprintk`, `ddlprintk`, `drsprintk`, `dsprintk`, `dctlprintk`, `dsasprintk`, `dmfprintk`, `dtsfprintk`, `dtransportprintk`, and `dTriggerDiagPrintk`.
- Dump helpers: `_debug_dump_mf()`, `_debug_dump_reply()`, and `_debug_dump_config()` interpret a buffer as little-endian dwords and print eight dwords per line with labels.

## Control Flow And Usage

Callers write debug code as a macro-wrapped command, for example `dctlprintk(ioc, ioc_info(...))`. At runtime the macro inspects `ioc->logging_level`; if the requested bit is not set, the command expression is not executed. The dump helpers are inline functions used when detailed frame/config visibility is needed. They loop over `sz` dwords, convert each with `le32_to_cpu()`, and emit the dump through `pr_info()`.

## State And Persistence Behavior

The header has no persistent state. It reads `IOC->logging_level`, which is maintained per adapter and is writable through the `logging_level` sysfs attribute implemented in `mpt3sas_ctl.c`. Logging choices persist only for the adapter lifetime or until changed by sysfs/module initialization.

## Dependencies And Integration Points

The macros assume `IOC` points to a `struct MPT3SAS_ADAPTER` with a `logging_level` field. The dump helpers require kernel logging and endian helpers. This header is included by mpt3sas implementation files that need debug gating; in this subset, `mpt3sas_ctl.c` uses `dctlprintk`, `dtmprintk`, and `_debug_dump_mf()` for ioctl/task-management diagnostics.

## Risks And Edge Cases

- Macro arguments can contain side effects; those side effects occur only when the logging bit is enabled.
- `MPT_CHECK_LOGGING` is a statement block macro, so callers must use it carefully in conditional contexts.
- `dsastransport` references `MPT_DEBUG_SAS_WIDE`, which is not defined in this header; it must be defined elsewhere or this macro is unsafe if used in a translation unit without that definition.
- Dump helpers trust the caller-provided size and pointer. Passing a short or invalid buffer can read beyond the intended frame.
- Excessive logging, especially frame dumps in hot paths, can flood kernel logs and perturb timing.

## Test Signals

Build coverage should compile all macro users and catch undefined logging bits such as `MPT_DEBUG_SAS_WIDE` if no external definition is present. Runtime tests can toggle the `logging_level` sysfs attribute and verify ioctl, task-management, config, reset, SCSI, and trigger diagnostics appear only for enabled bits. Fault-injection tests should avoid enabling broad frame dumps under high I/O load unless log-rate behavior is being explicitly evaluated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debugfs.c -->
# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debugfs.c

## Purpose

`mpt3sas_debugfs.c` implements the mpt3sas debugfs surface. It creates a global `mpt3sas` debugfs directory, per-adapter `scsi_hostN` directories, a binary-ish `ioc_dump` file that exposes the in-memory `struct MPT3SAS_ADAPTER`, and a `host_recovery` byte attribute. This is diagnostic-only infrastructure intended for kernel debugging and field support, not a stable user ABI.

## Important APIs, Types, And Functions

- Global root: `static struct dentry *mpt3sas_debugfs_root`.
- File operations: `mpt3sas_debugfs_iocdump_fops` wires `_debugfs_iocdump_open()`, `_debugfs_iocdump_read()`, and `_debugfs_iocdump_release()`.
- `_debugfs_iocdump_open()` allocates `struct mpt3sas_debugfs_buffer`, points `debug->buf` directly at the adapter object from `inode->i_private`, sets `debug->len` to `sizeof(struct MPT3SAS_ADAPTER)`, and stores it in `file->private_data`.
- `_debugfs_iocdump_read()` copies from `debug->buf` using `simple_read_from_buffer()`.
- `_debugfs_iocdump_release()` frees the small wrapper but not the adapter memory.
- `mpt3sas_init_debugfs()` creates `/sys/kernel/debug/mpt3sas`.
- `mpt3sas_exit_debugfs()` removes the global tree recursively.
- `mpt3sas_setup_debugfs()` creates per-adapter directory and files.
- `mpt3sas_destroy_debugfs()` removes the per-adapter tree recursively.

## Control Flow

Driver initialization calls `mpt3sas_init_debugfs()` once to create the root. Per adapter setup calls `mpt3sas_setup_debugfs(ioc)`, which names the directory `scsi_host%d` using `ioc->shost->host_no`, creates it under the root, creates `ioc_dump` with mode `0444` and `ioc` as private data, and creates a read-only `host_recovery` u8 file backed by `ioc->shost_recovery`.

When a user opens `ioc_dump`, debugfs passes the adapter pointer through `inode->i_private`. The open helper allocates an independent wrapper so reads can use `file->private_data`. Reads then return bytes from the live adapter structure, respecting file position. Release clears `private_data` and frees the wrapper. Teardown removes adapter or global directories recursively; debugfs handles file dentries.

## State And Persistence Behavior

Debugfs state is runtime-only. The root dentry is global. Each adapter stores `ioc->debugfs_root` and `ioc->ioc_dump` dentries. The `ioc_dump` buffer is not a snapshot: it is a pointer to the live `struct MPT3SAS_ADAPTER`, so repeated reads can observe changing fields. The wrapper allocated at open is per file descriptor and freed at release. `host_recovery` reads the current `ioc->shost_recovery` byte.

## Dependencies And Integration Points

The file depends on Linux debugfs, SCSI host structures, PCI/kernel types, and `mpt3sas_base.h` for `struct MPT3SAS_ADAPTER` and `struct mpt3sas_debugfs_buffer`. It integrates with the mpt3sas adapter lifecycle: setup must happen after `ioc->shost` and `ioc->pdev` are valid, and destroy must happen before or during adapter removal so debugfs no longer exposes freed adapter memory.

## Risks And Edge Cases

- `ioc_dump` exposes the raw in-kernel adapter structure, including pointers and layout-dependent data. This is useful for debugging but unsuitable as a stable ABI and potentially sensitive on systems where debugfs is accessible.
- The dump reads live memory without locking or snapshotting; concurrent adapter updates can produce inconsistent data.
- Lifetime safety depends on debugfs removal and open-file handling relative to adapter free. Because the wrapper points directly at `ioc`, stale opens during removal deserve scrutiny.
- Error handling logs failures but does not always clear partially created dentries. For example, if `ioc_dump` creation fails, it removes `ioc->debugfs_root` but does not reset the stored pointer in this file.
- If debugfs is disabled or unavailable, the create helpers may return error pointers on some kernels; consumers should align with kernel debugfs API expectations.

## Test Signals

With debugfs mounted, tests should verify `/sys/kernel/debug/mpt3sas` appears after driver init, per-host `scsi_hostN` directories appear after adapter setup, `ioc_dump` can be read and has `sizeof(struct MPT3SAS_ADAPTER)` bytes available through normal offset reads, and `host_recovery` reflects `ioc->shost_recovery`. Removal tests should open/read/release across adapter teardown and ensure no use-after-free or stale debugfs entries remain. Permission checks should confirm files are read-only (`0444`) and no stable parsing is assumed by tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_debugfs.c -->
