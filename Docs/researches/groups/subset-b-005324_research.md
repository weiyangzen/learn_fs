# subset-b-005324 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.c

## Purpose
`pmcraid.c` is the Linux SCSI low-level driver implementation for PMC Sierra MaxRAID PCI controllers. It binds the supported PCI adapter, allocates DMA command/control rings, exposes VSET and supported GSCSI resources as SCSI devices, handles SCSI I/O submission and completion, manages adapter reset/shutdown, and provides management/event surfaces through a character device, sysfs attributes, generic netlink AEN multicast, and fasync.

## Important APIs, types, and functions
The public kernel integration is through `pmcraid_driver`, `pmcraid_host_template`, module parameters `log_level`, `debug`, and `disable_aen`, and the char-device file operations in `pmcraid_fops`. Device lifecycle entry points are `pmcraid_probe()`, `pmcraid_remove()`, `pmcraid_shutdown()`, `pmcraid_suspend()`, and `pmcraid_resume()`. SCSI midlayer callbacks include `pmcraid_queuecommand()`, `pmcraid_sdev_init()`, `pmcraid_sdev_configure()`, `pmcraid_sdev_destroy()`, queue-depth control, and EH handlers for abort, device, bus, target, and host reset. Command allocation is centered on `pmcraid_get_free_cmd()`, `pmcraid_return_cmd()`, `_pmcraid_fire_command()`, and `pmcraid_send_cmd()`.

The main hardware protocol helpers are `pmcraid_identify_hrrq()`, `pmcraid_get_fwversion()`, `pmcraid_querycfg()`, `pmcraid_set_timestamp()`, and `pmcraid_set_supported_devs()`. HCAM asynchronous notification registration and cancellation are handled by `pmcraid_init_hcam()`, `pmcraid_send_hcam()`, `pmcraid_process_ccn()`, `pmcraid_process_ldn()`, and `pmcraid_unregister_hcams()`. Interrupt completion paths are split between `pmcraid_isr()`, `pmcraid_isr_msix()`, and `pmcraid_tasklet_function()`.

## Control flow
Probe enables the PCI function, requests BARs, maps BAR0, sets DMA masks, allocates a `Scsi_Host`, initializes the adapter instance and interrupts, allocates HRRQs/HCAM/config/command/control DMA buffers, determines reset type, enables interrupts, and performs `pmcraid_reset_bringup()`. Bringup is a command chain: HRRQ identify, firmware inquiry, query configuration table, initialize resource table, set timestamp, set supported devices, complete reset, register HCAMs, add the SCSI host, scan, create the char device, and schedule resource exposure.

The I/O path starts in `pmcraid_queuecommand_lck()`: reject or busy the request if the IOA is dead or resetting, complete unsupported `SYNCHRONIZE_CACHE` locally, fill an IOARCB from the SCSI CDB and resource handle, choose an HRRQ, build IOADLs from the SCSI scatterlist, and ring IOARRIN. The ISR acknowledges hardware events and schedules a tasklet. The tasklet consumes HRRQ entries while the toggle bit matches, finds the command by response handle, removes it from the pending pool, deletes timers, decrements outstanding count, and invokes the command completion. Normal SCSI completion runs through `pmcraid_io_done()` and `_pmcraid_io_done()`; error completions may synthesize sense data, issue REQUEST SENSE, cancel all, request sync completion, or report bus reset.

Reset flow is an explicit IOA state machine in `pmcraid_ioa_reset()`. It handles unknown, soft reset, hard reset, reset alert, bringdown, bringup, operational, and dead states. Timers, interrupts, tasklets, probe, suspend/resume, and SCSI EH can all enter this state machine, so callers coordinate with `host_lock`, `reset_wait_q`, `reset_cmd`, and `ioa_reset_in_progress`.

## State and persistence behavior
State is in memory only: per-adapter `pmcraid_instance`, DMA command/control buffers, HRRQ pointers and toggle bits, resource entries, pending/free command lists, reset flags, HCAM buffers, and char-device minor allocation. The driver persists no on-disk data. It does push transient state to firmware, including current timestamp and supported-device settings. User-visible state is exposed by sysfs attributes, the `/dev/pmcsasN` ioctl device, fasync registration, and generic netlink event multicast.

## Dependencies and integration points
This file depends on the PCI core, DMA APIs, SCSI midlayer, block queue limits, tasklets, workqueues, timers, generic netlink, char devices, sysfs class/device attributes, and firmware-specific register/command layouts from `pmcraid.h`. It integrates hardware interrupts with SCSI completion, CCN/LDN HCAM notifications with SCSI device add/remove and userspace AENs, and SCSI EH with firmware abort/reset commands.

## Risks and test signals
Important risks are concurrency around pending/free command lists, reset transitions entered from multiple contexts, DMA mapping/unmapping correctness, HRRQ toggle/index handling, command timeout recovery, lost CCN recovery, and user ABI validation for ioctls/netlink. `pmcraid_send_hcam()` assumes `pmcraid_init_hcam()` succeeds and would dereference NULL if no command block is available. `pmcraid_get_minor()` does not check for bitmap exhaustion before setting a bit, relying on the adapter count gate. Resume error paths call `scsi_host_put()` on an existing host, which warrants review. Practical test signals include PCI probe/remove with legacy INTx and MSI-X, forced reset through ioctl and SCSI EH, simulated IOASC error mapping, lost CCN handling, hot add/delete of resources, DMA scatterlist boundary cases, suspend/resume, and verifying no leaked command blocks after timeout/reset cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.h

## Purpose
`pmcraid.h` defines the firmware ABI, command formats, DMA structures, state containers, constants, logging tables, and ioctl ABI for `pmcraid.c`. It is not a generic exported API; it is the private contract between the MaxRAID driver implementation, SCSI midlayer data structures, and PMC IOA firmware.

## Important APIs, types, and functions
Key constants describe adapter identity, limits, command opcodes, request flags, resource types, IOASC parsing, timeouts, interrupt bits, doorbells, and reset states. Core firmware data structures include `struct pmcraid_ioadl_desc`, `pmcraid_ioarcb`, `pmcraid_ioasa`, `pmcraid_config_table_entry`, `pmcraid_config_table`, HCAM CCN/LDN layouts, and `pmcraid_control_block`. Driver-side structures include `pmcraid_cmd`, `pmcraid_interrupts`, `pmcraid_isr_param`, `pmcraid_hostrcb`, `pmcraid_instance`, and `pmcraid_resource_entry`.

The header also defines `pmcraid_ioasc_error_table`, `pmcraid_err()`, `pmcraid_info()`, `SCSI_CMD_TYPE()`, `IS_SCSI_READ_WRITE()`, `struct pmcraid_ioctl_header`, and `PMCRAID_IOCTL_RESET_ADAPTER`.

## Control flow relevance
The header is effectively the map used by the C file's state machine and I/O path. `pmcraid_cmd` binds a DMA control block, an optional SCSI command, list membership, completion, timer, callback, and scratch fields used by reset, abort, HRRQ identification, and sense handling. `pmcraid_instance` gathers all live adapter state: MMIO pointers, interrupt vectors, HRRQ buffers, command pools, resource lists, HCAM buffers, reset flags, outstanding command counters, and SCSI/PCI handles. Resource exposure and queuecommand use `pmcraid_resource_entry` to translate SCSI bus/target/lun to firmware resource handles.

## State and persistence behavior
The structures model volatile kernel and firmware state. Packed/aligned firmware structures must remain layout-compatible with the IOA. No durable storage is defined. User ABI persistence is limited to stable ioctl signature/type/number choices and the char-device naming constants.

## Dependencies and integration points
The header includes Linux completion/list/cdev and SCSI command headers plus generic netlink headers. It relies on QEMU-independent Linux kernel endian types and packed/aligned attributes. Firmware coupling is strong: bit numbering macros, response-handle toggle bits, register interrupt masks, IOASC encodings, and command opcodes are all hardware protocol definitions.

## Risks and test signals
Risks include ABI/layout drift in packed structures, endian misuse, duplicated or misspelled IOASC table entries, off-by-one limits in command/resource arrays, and macros that evaluate opcodes through GNU statement expressions. Changes should be validated with compile-time layout expectations where available, sparse/endian checks, SCSI command submission tests, ioctl ABI compatibility, and reset/interrupt tests that prove state constants still match `pmcraid.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ppa.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ppa.c

## Purpose
`ppa.c` is the low-level SCSI host adapter driver for the Iomega PPA3 parallel-port SCSI interface used by ZIP drives. It registers as a parport driver, probes compatible ports/devices, exposes one SCSI host per attached adapter, and runs a polled phase engine because the hardware does not provide normal interrupts.

## Important APIs, types, and functions
The central soft state is `ppa_struct`, which stores the parport device, base I/O port, selected transfer mode, current SCSI command, delayed work item, timeout/reconnect parameters, parport wait state, SCSI host pointer, and list node. Important parport helpers are `ppa_pb_claim()`, `ppa_pb_dismiss()`, `ppa_pb_release()`, `ppa_wakeup()`, and `got_it()`. Register-transfer helpers include `ppa_wait()`, `epp_reset()`, `ecp_sync()`, `ppa_byte_out()`, `ppa_byte_in()`, `ppa_nibble_in()`, `ppa_out()`, and `ppa_in()`.

Protocol sequencing is implemented by `ppa_connect()`, `ppa_disconnect()`, `ppa_select()`, `ppa_send_command()`, `ppa_completion()`, and `ppa_engine()`. SCSI integration comes from `ppa_template`, `ppa_queuecommand()`, `ppa_abort()`, `ppa_reset()`, and `ppa_biosparam()`. Device discovery and parport lifecycle are handled by `device_check()`, `ppa_init()`, `__ppa_attach()`, `ppa_attach()`, `ppa_detach()`, and `module_parport_driver()`.

## Control flow
When a parport appears, `__ppa_attach()` allocates `ppa_struct`, registers a parport device with a wakeup callback, claims the port, initializes the adapter, chooses I/O port count based on mode, allocates a SCSI host, links the host data back to `ppa_struct`, calls `scsi_add_host()`, and scans. `ppa_init()` autodetects NIBBLE, PS/2, or EPP modes from parport capabilities, performs connect/disconnect handshakes, pulses reset, and calls `device_check()`, which scans SCSI IDs with TEST UNIT READY and can fall back from attempted EPP to the old mode.

`ppa_queuecommand_lck()` accepts only one active command, initializes phase zero and default failure result, schedules delayed work, and attempts to claim the parport. `ppa_interrupt()` repeatedly calls `ppa_engine()`. The engine advances through phases for waiting on parport ownership, cable sanity check, target select, command send, scatterlist setup, data transfer, and final status/message read. `ppa_completion()` moves data in bursts for READ/WRITE commands but yields after about one jiffy to avoid monopolizing CPU. Successful or failed terminal states dismiss the parport and call `scsi_done()`.

## State and persistence behavior
State is in memory and port hardware registers. The driver has no durable persistence. Runtime tunables include the module-level `mode` parameter and proc write support for per-device `mode=` and `recon_tmo=`. The current command is stored in `dev->cur_cmd`, and phase/data-transfer position is held in the command-private `struct scsi_pointer`.

## Dependencies and integration points
The file depends on parport, low-level x86 I/O port helpers via `ppa.h`, delayed work, jiffies/udelay/mdelay timing, SCSI midlayer, scatterlist helpers, and legacy proc host-template hooks. It integrates parport arbitration with SCSI command serialization and uses PPA-specific handshakes to emulate a SCSI bus behind a parallel-port device.

## Risks and test signals
Risks include busy-wait CPU cost, fragile timing with old parallel-port chipsets, single-command serialization, no real abort after SCSI command issue, use of `sg_virt()` requiring CPU-addressable SG memory, EPP timeout handling, and detach while delayed work or `cur_cmd` is live. Useful tests include module load with each mode, autodetection fallback, no-device and cable-unplug paths, READ/WRITE scatterlist transfer across segments, SCSI EH abort/reset behavior, parport sharing contention, and detach/remove with no work left queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ppa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ppa.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/ppa.h

## Purpose
`ppa.h` is the private hardware-access header for the Iomega PPA3 parallel-port SCSI driver. It defines version/history metadata, transfer mode constants, timing/burst parameters, register access macros, and the internal `ppa_engine()` prototype used by `ppa.c`.

## Important APIs, types, and functions
The header defines mode constants `PPA_AUTODETECT`, `PPA_NIBBLE`, `PPA_PS2`, `PPA_EPP_8`, `PPA_EPP_16`, `PPA_EPP_32`, and `PPA_UNKNOWN`, plus `PPA_MODE_STRING`. Tunables include `PPA_BURST_SIZE`, `PPA_SELECT_TMO`, `PPA_SPIN_TMO`, `PPA_RECON_TMO`, and `PPA_DEBUG`. `IN_EPP_MODE()` identifies EPP variants. Register access macros wrap `inb()` and `outb()` for DTR, status, control, EPP data, FIFO, and ECR registers; `w_ctr()` optionally uses `outb_p()` when `CONFIG_SCSI_IZIP_SLOW_CTR` is enabled.

## Control flow relevance
`ppa.c` uses these constants to select transfer paths, set delays, poll ready/status bits, and drive the connect/disconnect/select handshakes. The register macros are the only abstraction between the protocol engine and hardware I/O ports.

## State and persistence behavior
No persistent state is stored here. The static `PPA_MODE_STRING` array has internal linkage because it is included directly by `ppa.c`. Runtime state lives in `ppa_struct` from `ppa.c`; this header only defines constants and I/O access forms.

## Dependencies and integration points
The header depends on Linux kernel headers for modules, I/O resources, delays, proc support, interrupts, SCSI host definitions, and architecture I/O. It must be included after `ppa_struct` is defined because it declares `ppa_engine(ppa_struct *, struct scsi_cmnd *)`.

## Risks and test signals
Risks include architecture dependence on port I/O, macro side effects, mode string array mutability, and timing constants that are empirical rather than negotiated. Validation should include compile coverage for both slow and normal control-port writes, transfer-mode selection tests, and hardware or emulated tests that exercise status/control bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ppa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ps3rom.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/ps3rom.c

## Purpose
`ps3rom.c` is the PlayStation 3 BD/DVD/CD-ROM SCSI driver. It presents a PS3 storage ROM device as an emulated SCSI host, translates SCSI packet and READ/WRITE_10 commands into PS3 LV1 storage hypervisor operations, and completes commands from the PS3 storage interrupt path.

## Important APIs, types, and functions
`struct ps3rom_private` stores the PS3 storage device and the single current SCSI command. `struct lv1_atapi_cmnd_block` is the hypervisor ATAPI command block. SCSI configuration is in `ps3rom_sdev_configure()`, which forces 10-byte MODE SENSE and READ/WRITE behavior. Command builders are `ps3rom_atapi_request()`, `ps3rom_read_request()`, and `ps3rom_write_request()`, with helpers `srb10_lba()` and `srb10_len()`. The SCSI queue entry is `ps3rom_queuecommand()`, completion runs through `ps3rom_interrupt()`, and device lifecycle is `ps3rom_probe()`, `ps3rom_remove()`, `ps3rom_init()`, and `ps3rom_exit()`.

## Control flow
Probe accepts only CD frame-sized block devices, allocates a 64 KiB GFP_DMA bounce buffer, calls `ps3stor_setup()` with `ps3rom_interrupt`, allocates a one-target/one-LUN SCSI host, stores the host in ps3 system-bus driver data, adds the host, and scans. Queueing stores the command as `curr_cmd`, dispatches READ_10 and WRITE_10 through direct `lv1_storage_read()`/`lv1_storage_write()`, and dispatches other commands as ATAPI packets through `lv1_storage_send_device_command()`. Write and ATAPI data-out paths copy from SCSI SG lists to the bounce buffer before issuing LV1 operations.

Interrupt completion calls `lv1_storage_get_async_status()`, checks the tag, fetches `curr_cmd`, copies bounce data back to the SCSI SG list on successful reads/data-in operations, sets residuals, decodes LV1 CHECK CONDITION status into SCSI sense data when possible, clears `curr_cmd`, and calls `scsi_done()`. Immediate command-submission failure builds ILLEGAL REQUEST sense and completes synchronously.

## State and persistence behavior
The driver is volatile and single-command (`can_queue = 1`). Persistent media state is outside the driver. The active async operation is correlated by `dev->tag` and `priv->curr_cmd`. Data staging uses `dev->bounce_buf`, `dev->bounce_lpar`, and `dev->bounce_size`.

## Dependencies and integration points
The file depends on PS3-specific system bus/storage helpers, LV1 hypervisor calls, SCSI midlayer, cdrom constants, highmem/slab allocation, and scatterlist copy helpers. It integrates with the PS3 storage core through `ps3stor_setup()`/`ps3stor_teardown()` and `ps3_system_bus_driver_register()`.

## Risks and test signals
Risks include relying on a single `curr_cmd`, tag mismatch only being logged, fixed 12-byte ATAPI packet copy regardless of CDB length, bounce-buffer size limiting max sectors, and error paths where an interrupt with no valid current command would be unsafe. Tests should cover probe rejection of non-CD frame block sizes, READ_10/WRITE_10 boundary sector counts, ATAPI non-data and data-in/out commands, LV1 policy-denied errors, CHECK CONDITION decoding, REQUEST_SENSE error handling, tag mismatch logging, remove after active command quiescence, and SG residual accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ps3rom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/Kconfig

## Purpose
This Kconfig entry exposes `CONFIG_QEDF`, the QLogic FastLinQ 41000-series FCoE offload initiator driver, as a tristate option.

## Important APIs, types, and functions
No C symbols are defined. The configuration symbol is `QEDF` with prompt `QLogic QEDF 25/40/100Gb FCoE Initiator Driver Support`. It depends on `PCI`, `SCSI`, `QED`, `LIBFC`, and `LIBFCOE`, and selects `QED_LL2` and `QED_FCOE`.

## Control flow
Build-system control flow is dependency-driven: the option is visible only when the required PCI, SCSI, QED, libfc, and libfcoe infrastructure is enabled. Enabling it forces lower-level QED LL2 and FCoE support so the driver can bind to hardware and offload FCoE traffic.

## State and persistence behavior
The file has no runtime state. Its persistent effect is kernel configuration state in `.config`, which determines whether `qedf.o` is built in, built as a module, or omitted.

## Dependencies and integration points
It integrates the driver into the kernel's SCSI and FCoE stacks and into QED core support. The selected options imply that QEDF relies on QED firmware/hardware services plus libfc/libfcoe protocol layers.

## Risks and test signals
The main risks are dependency drift and accidental prompt invisibility or missing selected transport support. Test signals are Kconfig resolution for built-in and module builds, compile coverage with `QEDF=m` and `QEDF=y`, and verification that disabling `QED`, `LIBFC`, or `LIBFCOE` correctly hides or rejects QEDF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/Makefile

## Purpose
This Makefile defines the QEDF driver object composition for the kernel build.

## Important APIs, types, and functions
`obj-$(CONFIG_QEDF) := qedf.o` builds the aggregate object when the Kconfig symbol is enabled. `qedf-y` lists the core objects: debug, main, I/O, FIP, attributes, ELS, SCSI firmware helpers, and FCoE firmware helpers. `qedf-$(CONFIG_DEBUG_FS)` conditionally adds debugfs support.

## Control flow
The build assembles one `qedf.o` from the listed objects. Debugfs code is included only when both QEDF is built and `CONFIG_DEBUG_FS` is enabled.

## State and persistence behavior
There is no runtime state. The file influences generated build artifacts and module contents.

## Dependencies and integration points
It connects the firmware-helper files in this work item, `drv_scsi_fw_funcs.o` and `drv_fcoe_fw_funcs.o`, into the broader QEDF module. It also makes debugfs support an optional build-time integration point.

## Risks and test signals
Risks are omitted objects causing unresolved symbols, stale object names after source moves, or debugfs-only code accidentally required by non-debug builds. Test signals are clean `CONFIG_QEDF=m/y` builds with and without `CONFIG_DEBUG_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.c

## Purpose
`drv_fcoe_fw_funcs.c` initializes QEDF FCoE firmware task contexts and SQEs for read/write initiator I/O, midpath/unsolicited exchanges, aborts, cleanup, and sequence recovery. It is a formatting layer between QEDF driver logic and QED firmware HSI structures.

## Important APIs, types, and functions
The local helper `init_common_sqe()` clears the SQE, sets `FCOE_WQE_REQ_TYPE`, and assigns `task_id`. Exported helpers are `init_initiator_rw_fcoe_task()`, `init_initiator_midpath_unsolicited_fcoe_task()`, `init_initiator_abort_fcoe_task()`, `init_initiator_cleanup_fcoe_task()`, and `init_initiator_sequence_recovery_fcoe_task()`. They use `struct fcoe_task_params`, `struct scsi_sgl_task_params`, `struct regpair`, FCoE task contexts, and helper functions from `drv_scsi_fw_funcs.c`.

## Control flow
For read/write I/O, the function preserves the ystorm aggregate validation byte, clears the context, determines fast versus slow SGL mode with `scsi_is_slow_sgl()`, computes transfer size from task type, and fills ystorm, tstorm, ustorm, and mstorm context regions. Write tasks configure TX SGLs and expect first transfer. Read tasks configure RX SGLs and data remaining. Both paths set response/sense buffer addresses and initialize a `SEND_FCOE_CMD` SQE.

Midpath initialization clears context, sets TX and RX SGL context, copies FC header parameters, configures whether firmware places the FC header, initializes connection/CQ/task-type fields, and emits a `SEND_FCOE_MIDPATH` SQE with burst length, SGE count, and fast SGL mode. Abort, cleanup, and sequence recovery only initialize common SQE fields, with sequence recovery also writing the desired offset.

## State and persistence behavior
All state is written into caller-provided firmware context and SQE memory. There is no allocation, global state, persistence, locking, or I/O. The functions assume input structures and DMA addresses have already been prepared by the caller.

## Dependencies and integration points
The file depends on `drv_fcoe_fw_funcs.h`, `drv_scsi_fw_funcs.h`, QEDF HSI definitions, endian conversion helpers, and firmware bitfield macros such as `SET_FIELD`. It is integrated into `qedf.o` and likely called by QEDF I/O submission and ELS/FIP paths before ringing hardware queues.

## Risks and test signals
Risks include HSI layout drift, wrong endian conversion, invalid task type/size pairing, unvalidated pointers, mismatched slow-SGL mode constants between TX/RX fields, and preserving only one aggregate context byte across clear. Tests should check generated context bytes against firmware specifications for read, write, tape, slow SGL, fast SGL, midpath with/without FC header placement, abort, cleanup, and sequence recovery. Static analysis should focus on null pointer assumptions and struct size changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.h

## Purpose
`drv_fcoe_fw_funcs.h` declares the QEDF FCoE firmware-context initialization API and defines `struct fcoe_task_params`, the common input/output bundle used by those helpers.

## Important APIs, types, and functions
`struct fcoe_task_params` carries output pointers to a `fcoe_task_context` and `fcoe_wqe`, plus task type, TX/RX byte counts, connection CID, initiator task id, CQ RSS number, and disk/tape device classification. Declared functions initialize read/write tasks, midpath unsolicited tasks, abort tasks, cleanup tasks, and sequence recovery tasks.

## Control flow relevance
Callers fill `fcoe_task_params` and SGL-related inputs, call one of the init functions, then submit the resulting SQE/context to firmware through QEDF queueing code elsewhere. The header documents which buffers and payloads are caller-provided.

## State and persistence behavior
The header defines no storage. It describes write targets in caller-owned memory and has no persistence behavior.

## Dependencies and integration points
It includes `drv_scsi_fw_funcs.h`, `qedf_hsi.h`, and QED interface headers. That makes it tightly coupled to firmware HSI structures and common QED storage types.

## Risks and test signals
Risks include stale comments, misspelled parameter names, and ABI drift if HSI structs change without updating helper signatures. Test signals include successful compilation of all QEDF objects, call-site type checking, and context-layout tests in the C implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_fcoe_fw_funcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.c

## Purpose
`drv_scsi_fw_funcs.c` provides common SCSI scatter-gather helper routines for QEDF firmware context initialization. It determines when firmware should use slow SGL handling and copies SGL metadata plus cached SGEs into HSI context structures.

## Important APIs, types, and functions
`scsi_is_slow_sgl()` returns true when the SGL exceeds the slow-SGL threshold and contains a small middle SGE. `init_scsi_sgl_context()` fills `struct scsi_sgl_params` and the cached `struct scsi_cached_sges` entries from caller-provided `struct scsi_sgl_task_params`.

## Control flow
`init_scsi_sgl_context()` copies the physical SGL address, total byte length, and SGE count into little-endian context fields. It then copies up to four cached SGE descriptors into the firmware context, converting address halves and lengths to little endian. Callers in `drv_fcoe_fw_funcs.c` invoke this for TX and RX data descriptors depending on task type.

## State and persistence behavior
The file has no global state, allocation, locking, persistence, or hardware I/O. It mutates only caller-provided context memory.

## Dependencies and integration points
It depends on `drv_scsi_fw_funcs.h`, QED common/storage/FCoE HSI types, and endian conversion helpers. It is linked into QEDF and used by FCoE task initialization.

## Risks and test signals
Risks include trusting `sgl_task_params->sgl` without null/length validation, using a fixed cached-SGE count of four, and threshold mismatches with firmware expectations. Tests should cover zero, one, four, and more-than-four SGEs; small middle SGE detection; endian conversion of addresses and lengths; and use by both read and write FCoE task setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.h

## Purpose
`drv_scsi_fw_funcs.h` defines common QEDF SCSI firmware-helper parameter structures and declares helper functions for SGL context initialization.

## Important APIs, types, and functions
`struct scsi_sgl_task_params` describes an SGL pointer, SGL physical address, total buffer size, SGE count, and whether a small middle SGE exists. `struct scsi_dif_task_params` describes DIF/protection settings, including reference/application tags, guard/protection modes, validation/forwarding flags, and connection-error behavior. `struct scsi_initiator_cmd_params` describes extended CDB and sense-data-buffer parameters. The declared functions are `scsi_is_slow_sgl()` and `init_scsi_sgl_context()`.

## Control flow relevance
FCoE firmware helpers use this header to classify SGLs and populate the SGL-related areas of ystorm/mstorm contexts. DIF and initiator command parameter structures are available to higher-level helpers even though this specific C file only uses SGL fields.

## State and persistence behavior
The header has no storage or durable state. It describes caller-owned parameters and firmware-context output fields.

## Dependencies and integration points
It includes QED common HSI, storage common, and FCoE common headers, binding the helper API to QED firmware structures. It is included by both FCoE helper C/H files.

## Risks and test signals
Risks include structure field drift against firmware HSI, unused DIF fields becoming stale, and callers passing inconsistent `num_sges`, `total_buffer_size`, and SGL pointer values. Test signals include compile coverage, static analysis of all call sites, slow-SGL threshold tests, and firmware-context byte comparison for representative SGL layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qedf/drv_scsi_fw_funcs.h -->
