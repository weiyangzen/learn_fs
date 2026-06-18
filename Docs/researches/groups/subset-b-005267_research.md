# Research Group: subset-b-005267

This grouped report covers HP Smart Array HPSA controller headers, the HighPoint RocketRAID IOP SCSI driver and protocol header, and the IBM virtual SCSI makefile. Each file section is bounded with reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hpsa.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/hpsa.h

## Purpose

`hpsa.h` is the private controller and host-state header for the HP Smart Array SAS driver. It defines the `ctlr_info` controller object, discovered-device records, SAS transport helper structures, reply queue buffers, BMIC controller-parameter payloads, controller event flags, reset constants, MMIO register offsets, and inline access-method implementations for simple, performant, and I/O accelerator controller modes.

## Important APIs, Types, and Functions

- `struct access_method` abstracts hardware submission, interrupt masking, pending-interrupt detection, and completion retrieval through `submit_command`, `set_intr_mask`, `intr_pending`, and `command_completed`.
- `struct hpsa_scsi_dev_t` is the driver's discovered-device model. It carries OS-visible bus/target/LUN, hardware SCSI-3 address, VPD/device ID data, SAS address, RAID level/offline status, queue-depth counters, reset state, I/O accelerator handles and offload flags, RAID map data, physical-disk backpointers for logical volumes, abort support, SAS port linkage, and external-array status.
- `struct ctlr_info` is the main per-controller state. It stores PCI/MMIO identity, command limits, interrupt mode, SCSI host pointer, device table protected by `devlock`, command/error DMA pools, scan wait state, performant-mode transition tables, reply queues, block-fetch tables, accelerator support, heartbeat/lockup monitoring fields, delayed work items, IRQ names/queue IDs, task-management support bits, event flags, offline-device list, reset locks, SAS host, and workqueues.
- `struct reply_queue_buffer` tracks a DMA-visible reply queue head, bus address, current index, size, and wrap bit.
- Static access methods include `SA5_submit_command*()`, `SA5_intr_mask()`, `SA5B_intr_mask()`, `SA5_performant_intr_mask()`, `SA5_completed()`, `SA5_performant_completed()`, `SA5_ioaccel_mode1_completed()`, and interrupt-pending helpers.
- Prebuilt `struct access_method` instances (`SA5_access`, `SA5B_access`, `SA5_performant_access`, `SA5_ioaccel_mode1_access`, `SA5_ioaccel_mode2_access`, etc.) bind board families or transport modes to the proper register protocol.
- `struct board_type` maps PCI board IDs to product names and access methods.

## Control Flow and State

The header's inline control flow is the low-level command/completion path. Submission writes a command bus address to the request port, sometimes followed by a scratchpad read to flush posted writes. Interrupt mask functions invert the controller-specific semantics where zero enables and mode-specific bits disable interrupts. Simple completion reads the reply port and decrements `commands_outstanding` for non-empty entries. Performant completion consumes entries from `reply_queue[q]`, validates the wrap bit in the low reply word, clears outbound doorbell state for non-MSI/MSI-X use, advances `current_entry`, toggles `wraparound` at the queue end, and decrements outstanding commands. I/O accelerator mode 1 completion uses a ring entry value of `IOACCEL_MODE1_REPLY_UNUSED`, clears consumed entries, writes the consumer index, and maintains the same outstanding-command accounting.

Persistent runtime state is memory resident in `ctlr_info` and `hpsa_scsi_dev_t`; it is rebuilt during probe and discovery rather than persisted to disk. The driver does cache controller firmware capabilities, task-management flags, event bits, heartbeat samples, device offload configuration, offline-device entries, and SAS topology structures across workqueue ticks while the controller is bound.

## Dependencies and Integration Points

`hpsa.h` depends on Linux SCSI/SAS, PCI, DMA, workqueue, waitqueue, atomic, spinlock, and MMIO primitives supplied by surrounding driver includes, plus command ABI definitions from `hpsa_cmd.h`. It integrates with the HPSA C implementation that allocates command pools, fills CISS command records, handles SCSI mid-layer callbacks, drives SAS transport registration, monitors controller events, performs rescans, handles resets, and chooses an `access_method` from the board table.

## Risks

- The inline MMIO functions encode hardware-specific ordering requirements; removing readbacks or write memory barriers can create lost commands or stale completions on posted-write architectures.
- Completion accounting relies on every non-empty completion decrementing `commands_outstanding`; mismatches can break lockup detection, reset waits, or queue throttling.
- `hpsa_scsi_dev_t` mixes logical-volume, physical-disk, SAS, and I/O accelerator state, so discovery/rescan changes must preserve lock discipline around `devlock`, reset flags, and physical-disk reference arrays.
- Reply queue wrap handling assumes `h->max_commands` matches the allocated performant queue depth, while I/O accelerator mode 1 uses `rq->size`; mode confusion would corrupt ring traversal.
- Controller event flags trigger rescans and offload reconfiguration. Missed event bits can leave stale topology or accelerator maps.

## Test Signals

- Build coverage with HPSA enabled verifies that command ABI types and controller fields match the implementation.
- Probe tests should exercise simple, performant, and I/O accelerator-capable boards, confirming interrupt enable/disable and command completion under MSI-X and non-MSI modes.
- Runtime signals include stable `commands_outstanding`, no reply queue wrap stalls, successful discovery of logical/physical devices, SAS transport objects, rescan on event bits, and clean controller reset/abort behavior.
- Fault-injection or hardware tests should cover controller lockup detection, offline-device handling, I/O accelerator disable/config-change events, and task-management support flag parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hpsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hpsa_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/hpsa_cmd.h

## Purpose

`hpsa_cmd.h` defines the packed CISS/HPSA command ABI shared between the Smart Array driver and controller firmware. It supplies status codes, SCSI/BMIC opcodes, LUN encodings, command-list and error-info layouts, I/O accelerator mode 1 and mode 2 command formats, task-management request formats, configuration/transport tables, RAID map structures, report-LUN payloads, and large BMIC identify/sense data structures.

## Important APIs, Types, and Functions

- Status and task-management constants include `CMD_SUCCESS`, `CMD_TARGET_STATUS`, transport and hardware error codes, driver-local `CMD_CTLR_LOCKUP`, and `CISS_TMF_*` result values.
- SCSI/VPD/BMIC constants define inquiry/report opcodes, logical-volume state values, cache flush and firmware flash commands, physical-device identify commands, diagnostic options, and subsystem/storage-box sense commands.
- `struct raid_map_data` and `struct raid_map_disk_data` describe logical-to-physical accelerator mapping, encryption flags, disk layout, striping, row counts, and per-entry I/O accelerator handles.
- `struct ReportLUNdata`, `struct ext_report_lun_entry`, and `struct ReportExtendedLUNdata` define logical and extended physical LUN discovery payloads.
- `union LUNAddr`, `union SCSI3Addr`, `struct PhysDevAddr`, and `struct LogDevAddr` encode the 8-byte CISS LUN address formats used in command headers.
- `struct CommandListHeader`, `struct RequestBlock`, `struct ErrDescriptor`, `struct SGDescriptor`, `union MoreErrInfo`, and `struct ErrorInfo` form the normal CISS command, S/G, and error contract.
- `struct CommandList` wraps the hardware command record with driver-private state: bus address, controller pointer, command type, command index, completion wait, Linux `scsi_cmnd`, work item, accelerator physical-disk pointer, retry flag, device pointer, and an aligned `atomic_t refcount`.
- `struct io_accel1_cmd`, `struct io_accel2_cmd`, `struct ioaccel2_sg_element`, and `struct io_accel2_scsi_response` define bypass command formats and completion/error responses.
- `struct hpsa_tmf_struct` defines I/O accelerator mode 2 task-management requests.
- `struct CfgTable` and `struct TransTable_struct` expose firmware transport capabilities, active mode, command limits, heartbeat, driver support, task-management support, event notify bits, block-fetch values, reply queue count/size, and reply queue addresses.
- `struct bmic_identify_controller`, `struct bmic_identify_physical_device`, `struct bmic_sense_subsystem_info`, and `struct bmic_sense_storage_box_params` carry detailed firmware inventory, physical-drive, enclosure, health, endurance, path, and encryption-key metadata.

## Control Flow and State

This header contains no executable driver flow beyond a compile-time `static_assert` that keeps `CommandList.refcount` properly aligned for architectures that reject unaligned atomics. Runtime flow is imposed by the C files that allocate these structures in DMA-coherent memory, fill little-endian fields, submit them through the access methods in `hpsa.h`, and interpret the returned `ErrorInfo` or accelerator response. The ABI state is mostly transient per command, but `CfgTable`, `TransTable_struct`, report-LUN data, RAID maps, and BMIC identify data are cached by the driver to shape topology, queue limits, offload decisions, and health reporting.

## Dependencies and Integration Points

The file depends on Linux fixed-width types, endian annotations, packing/alignment attributes, `BUILD_BUG`/`static_assert` support, `atomic_t`, `struct scsi_cmnd`, `struct completion`, and HPSA-private forward declarations. It is consumed by `hpsa.h` and the HPSA implementation whenever commands are allocated, initialized, DMA-mapped, submitted, completed, or decoded. The structures are also the contract with controller firmware, so their packing and byte ordering are integration points as important as C function signatures.

## Risks

- Packed hardware structures are layout-sensitive; changing field order, alignment, sizes, or endian conversions can break firmware communication.
- `CommandList` must remain 128-byte aligned and keep `refcount` naturally aligned despite containing packed hardware substructures.
- CISS completion tags reuse low address bits for mode/error/block-fetch metadata, so command pool alignment and tag masking must remain consistent with `COMMANDLIST_ALIGNMENT`, `DIRECT_LOOKUP_SHIFT`, and mode-specific command types.
- Large BMIC structures encode many firmware-defined offsets. Partial initialization or short DMA buffers can misinterpret drive health, encryption, path, or enclosure data.
- Accelerator command paths have separate S/G limits and response formats. Mixing normal CISS, ioaccel1, and ioaccel2 fields risks bad DMA, missing sense data, or incorrect residual reporting.

## Test Signals

- Compile-time assertions and `sizeof`/offset-sensitive build coverage should catch accidental alignment regressions.
- Hardware or emulator tests should validate inquiry/report-LUN discovery, BMIC identify/controller parameter commands, normal CISS S/G I/O, and both I/O accelerator modes when supported.
- Fault-path tests should inspect sense copying, residual counts, task-management responses, accelerator-disabled status, and controller lockup marking.
- Discovery tests should confirm RAID map parsing, physical-drive inventory, logical-volume status states, encryption flags, and queue-depth limits derived from BMIC data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hpsa_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hptiop.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/hptiop.c

## Purpose

`hptiop.c` is the Linux SCSI low-level driver for HighPoint RocketRAID 3xxx/4xxx PCI controllers. It binds PCI IDs to one of three IOP adapter families, maps their MMIO/mailbox interfaces, negotiates firmware configuration, allocates DMA request blocks, implements the SCSI queue/completion path, handles interrupts and messages, exposes version attributes, performs host reset/shutdown, and registers the module's PCI and SCSI driver interfaces.

## Important APIs, Types, and Functions

- Adapter-family operations are collected in `hptiop_itl_ops`, `hptiop_mv_ops`, and `hptiop_mvfrey_ops`, each supplying `iop_wait_ready`, internal memory allocation/free, BAR mapping, interrupt control, config get/set, interrupt processing, message posting, request posting, DMA address width, reset-communication behavior, and host physical-address flags.
- Ready/config paths include `iop_wait_ready_itl()`, `iop_wait_ready_mv()`, `iop_wait_ready_mvfrey()`, `iop_get_config_*()`, `iop_set_config_*()`, `iop_send_sync_request_*()`, and `iop_send_sync_msg()`.
- Interrupt paths include `iop_intr_itl()`, `iop_intr_mv()`, `iop_intr_mvfrey()`, `hptiop_intr()`, outbound queue drain helpers, family-specific request callbacks, and `hptiop_message_callback()`.
- Request management functions include `get_req()`, `free_req()`, `hptiop_buildsgl()`, `hptiop_post_req_itl()`, `hptiop_post_req_mv()`, `hptiop_post_req_mvfrey()`, and `hptiop_finish_scsi_req()`.
- SCSI mid-layer entry points are exposed through `driver_template`: `hptiop_queuecommand`, `hptiop_reset`, `hptiop_info`, `hptiop_adjust_disk_queue_depth`, and `hptiop_sdev_configure`.
- PCI/module lifecycle is implemented by `hptiop_probe()`, `hptiop_remove()`, `hptiop_shutdown()`, `hptiop_module_init()`, and `hptiop_module_exit()`.
- Sysfs host attributes `driver-version` and `firmware-version` are provided through `hptiop_show_version()` and `hptiop_show_fw_version()`.

## Control Flow and State

Module initialization registers `hptiop_pci_driver`. Probe enables the PCI device, sets bus mastering and a DMA mask based on the matched adapter ops, requests PCI regions, allocates a `Scsi_Host` with `struct hptiop_hba` hostdata, maps family-specific BARs, waits for firmware readiness, allocates family-internal memory where needed, gets firmware configuration, records max request/device/S/G and version limits, optionally resets MVFREY communication rings, configures the firmware with host ID and max request size, requests the shared IRQ, allocates one DMA-coherent request buffer per firmware request slot, initializes the free-list, starts IOP background tasks, adds the SCSI host, and scans.

The normal I/O path starts at `hptiop_queuecommand_lck()`. It pops a request from `hba->req_list`, rejects out-of-range channel/target/LUN combinations with `DID_BAD_TARGET`, maps the Linux S/G list with `scsi_dma_map()`, fills an `IOP_REQUEST_TYPE_SCSI_COMMAND` request with CDB, target address, data length, S/G entries, pending result, and size, then posts it through the selected adapter ops. Completion arrives via IRQ polling of family-specific outbound queues or doorbells. The request callback decodes the tag/index, normalizes success bits for newer queue formats, and calls `hptiop_finish_scsi_req()`, which unmaps DMA, converts firmware result codes to Linux `DID_*` or check-condition status, copies sense data from the request payload for `IOP_RESULT_CHECK_CONDITION`, calls `scsi_done()`, and returns the request to the free-list.

Synchronous messages and config requests disable interrupts or poll the family interrupt handler while waiting for `hba->msg_done`. Reset posts `IOPMU_INBOUND_MSG0_RESET`, waits up to 60 seconds for `reset_wq`, then restarts background tasks. Shutdown sends `IOPMU_INBOUND_MSG0_SHUTDOWN` and disables outbound interrupts. Remove calls `scsi_remove_host()`, shutdown, IRQ free, request DMA free, internal memory free, BAR unmap, PCI region release, PCI disable, and `scsi_host_put()`.

## State and Persistence Behavior

All state is volatile kernel/device state. `struct hptiop_hba` persists while the PCI device is bound and stores adapter ops, mapped register pointers, firmware limits and versions, request size, free-list head, request array, DMA allocations, reset counters, flags (`initialized`, `iopintf_v2`, `msg_done`), and wait queues. Per-command private state lives in `struct hpt_cmd_priv` attached to each `scsi_cmnd`, tracking DMA mapping and S/G count. Firmware configuration is read at probe and written through `SET_CONFIG`, but the driver does not persist settings to filesystem storage.

## Dependencies and Integration Points

The driver integrates with Linux PCI APIs, DMA coherent allocation and streaming S/G mapping, interrupt registration, SCSI mid-layer host templates, queue limits, sysfs host attribute groups, wait queues, atomics, MMIO helpers, and module registration. It depends on `hptiop.h` for firmware request/register layouts and adapter state definitions. Hardware integration is split by adapter family: Intel-style queue registers, Marvell memory queues, and MVFREY inbound/outbound list rings.

## Risks

- `get_req()` and `free_req()` manipulate `hba->req_list` without internal locking and rely on the SCSI host lock held by queue and interrupt paths. Any future call outside that lock could corrupt the free-list.
- Several error paths in probe jump to `unmap_pci_bar` after family-internal memory allocation failures, relying on `internal_memfree()` to tolerate unallocated state. The MV and MVFREY implementations return `-1` for missing memory but are otherwise benign.
- `hptiop_buildsgl()` uses `BUG_ON()` for DMA mapping failures and S/G overflow, turning recoverable resource pressure into a kernel crash.
- Sense data for check condition is copied from `req->sg_list`, so the firmware ABI must place sense data there for that result. Any ABI change would corrupt sense reporting.
- MVFREY ring pointer toggling and tag encoding are hand-coded and sensitive to list count, shifted physical address width, and ordering of writes/readbacks.
- `hptiop_intr()` returns an integer `handled` as `irqreturn_t`; the values align with `IRQ_NONE`/`IRQ_HANDLED`, but changes should preserve that convention.

## Test Signals

- Build with `CONFIG_SCSI_HPTIOP` should validate SCSI template, PCI ID, queue-limit, and DMA APIs.
- Probe tests on each family should confirm BAR mapping, DMA mask selection, config read/write, IRQ registration, background-task start, and SCSI scan.
- I/O tests should cover reads/writes with no data, single S/G, and many S/G segments up to `max_sg_descriptors`, verifying residuals and DMA unmap.
- Fault tests should induce busy, bad target, reset, invalid request, fail, and check-condition firmware results and confirm Linux result mapping and sense propagation.
- Reset/remove/shutdown tests should verify wait-queue wakeup, interrupt disable, request-memory cleanup, and no completions after `scsi_remove_host()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hptiop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hptiop.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/hptiop.h

## Purpose

`hptiop.h` is the private protocol and state header for the HighPoint RocketRAID IOP driver. It defines the memory-mapped register blocks, queue constants, firmware message and request formats, S/G descriptors, per-request and per-command private state, adapter-family enum, per-HBA state, ioctl context, adapter-ops vtable, and debug/result macros used by `hptiop.c`.

## Important APIs, Types, and Functions

- Register layouts include `struct hpt_iopmu_itl` for Intel-style mailboxes/queues, `struct hpt_iopmu_mv` and `struct hpt_iopmv_regs` for Marvell queues/doorbells, and `struct hpt_iopmu_mvfrey` plus `mvfrey_inlist_entry`/`mvfrey_outlist_entry` for MVFREY list-based communication.
- Queue and interrupt constants define empty queue values, host-address marker bits, request-size/result bits, message/postqueue interrupt bits, MV queue length, MVFREY pointer toggles, and doorbell message bits.
- `enum hpt_iopmu_message` lists host-to-IOP control messages such as NOP, reset, flush, shutdown, stop/start background task, and reset communication, plus outbound device registration/unregistration/revalidation ranges.
- `struct hpt_iop_request_header` is the common firmware request header carrying size, type, flags, result, and 64-bit host context split into two fields.
- `enum hpt_iop_request_type` and `enum hpt_iop_result_type` describe GET_CONFIG, SET_CONFIG, block, SCSI, ioctl requests, and their completion status values.
- Request payloads include `hpt_iop_request_get_config`, `hpt_iop_request_set_config`, `hpt_iop_request_block_command`, `hpt_iop_request_scsi_command`, and `hpt_iop_request_ioctl_command`.
- `struct hptiop_request` tracks a host request slot, virtual request buffer, shifted DMA address, active `scsi_cmnd`, and index.
- `struct hpt_cmd_priv` is the SCSI command-private extension used through `HPT_SCP(scp)` to remember DMA mapping and S/G count.
- `struct hptiop_hba` stores family-specific register and internal-memory pointers in a union, Linux host and PCI pointers, firmware limits, flags, free-list and request arrays, DMA allocations, atomics, and wait queues.
- `struct hptiop_adapter_ops` is the family vtable consumed by the C file for BAR mapping, interrupt control, config I/O, request/message posting, reset communication, and DMA addressing policy.

## Control Flow and State

The header itself has no executable flow, but it encodes the state machines used by the driver. Firmware requests start as a common header with `IOP_RESULT_PENDING`, get posted through a family queue with an encoded host context, and return through outbound queues/doorbells with the same context. Messages use the `IOPMU_INBOUND_MSG0_*` namespace and complete by setting `msg_done` in the HBA. The HBA state persists from PCI probe to remove and holds all per-adapter queue, request, DMA, and reset state needed by `hptiop.c`.

## Dependencies and Integration Points

This header assumes Linux endian types, DMA address types, SCSI command structures, atomic and waitqueue types, and MMIO annotations are available from the including C file. It is tightly coupled to `hptiop.c` and to HighPoint firmware ABIs for RocketRAID 3xxx/4xxx controllers. It also bridges the SCSI mid-layer through `struct scsi_cmnd`, `Scsi_Host`, and per-command private storage.

## Risks

- Register structs are hardware ABI overlays; packing, reserved array sizes, and field offsets must remain exact.
- The request header's `context`/`context_hi32` fields are reused differently by adapter families, so shared code must not assume one encoding.
- `HPTIOP_MAX_REQUESTS` caps the static request array at 256 even if firmware advertises more; probe correctly clamps but future changes must keep allocation and tag decoding aligned.
- Flexible-array request payloads require careful `struct_size()` calculations to avoid request-buffer overflow.
- `HPT_SCP()` depends on `driver_template.cmd_size` matching `sizeof(struct hpt_cmd_priv)`.

## Test Signals

- Compile coverage of `hptiop.c` validates register and request layout references.
- Probe-time config should confirm firmware values populate `hptiop_hba` fields and that max requests are clamped to `HPTIOP_MAX_REQUESTS`.
- Family-specific hardware tests should validate ITL, MV, and MVFREY message, postqueue, and completion paths.
- DMA/SCSI tests should verify `hpt_cmd_priv` mapping state, S/G descriptor eot markers, request-size calculations, and context tag round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hptiop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/Makefile

## Purpose

`ibmvscsi/Makefile` is the Kbuild fragment for IBM virtual SCSI drivers. It conditionally builds the classic IBM virtual SCSI adapter object and the IBM virtual Fibre Channel object based on kernel configuration symbols.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SCSI_IBMVSCSI) += ibmvscsi.o` adds the IBM virtual SCSI driver object when `CONFIG_SCSI_IBMVSCSI` is enabled as built-in or module.
- `obj-$(CONFIG_SCSI_IBMVFC) += ibmvfc.o` adds the IBM virtual Fibre Channel driver object when `CONFIG_SCSI_IBMVFC` is enabled.
- The file also carries the `GPL-2.0-only` SPDX tag expected by kernel source policy.

## Control Flow and State

There is no runtime control flow or persisted state in this file. Kbuild evaluates the `obj-*` assignments during kernel build generation and includes the requested objects in either built-in archives or module builds depending on each configuration symbol's value.

## Dependencies and Integration Points

The file integrates with the Linux kernel build system under `drivers/scsi/Makefile` and the Kconfig symbols that expose IBM virtual SCSI and IBM virtual Fibre Channel support. The actual driver behavior lives in the corresponding C sources; this Makefile only controls compilation inclusion.

## Risks

- Incorrect config symbol names would silently drop driver objects from builds.
- Adding multi-object drivers here would require converting each target to `<module>-y` style lists; the current two one-line targets assume single composite objects already defined by their source names.
- Build coverage depends on both symbols being tested as built-in and module where supported.

## Test Signals

- `make M=drivers/scsi/ibmvscsi` or an equivalent in-tree build with `CONFIG_SCSI_IBMVSCSI=m` should produce `ibmvscsi.ko`.
- A build with `CONFIG_SCSI_IBMVFC=m` should produce `ibmvfc.ko`.
- Built-in configurations should include the objects in the relevant `built-in.a` without missing-object Kbuild warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/ibmvscsi/Makefile -->
