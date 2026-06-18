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
