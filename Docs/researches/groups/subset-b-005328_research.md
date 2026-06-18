# Research: subset-b-005328

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla1280.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla1280.h

## Purpose
`qla1280.h` is the private hardware contract for the legacy QLogic ISP1280/ISP12160 parallel SCSI host adapter driver. It does not implement executable control flow itself; instead it defines the register layout, mailbox protocol constants, NVRAM image layout, request/response IOCB formats, status codes, and the driver's core `struct scsi_qla_host` state used by the matching C driver.

## Important APIs, Types, and Constants
- `RD_REG_WORD`, `RD_REG_WORD_dmasync`, and `WRT_REG_WORD` abstract register access over either memory-mapped I/O or port I/O, depending on `MEMORY_MAPPED_IO`.
- `struct srb` is the per-command SCSI Request Block stored behind each `struct scsi_cmnd`. It carries the command pointer, completion wait hook, saved DMA handle, data direction, and flags such as `SRB_TIMEOUT`, `SRB_SENT`, `SRB_ABORT_PENDING`, and `SRB_ABORTED`.
- `struct device_reg` maps the ISP device register block, including PCI/device IDs, config words, interrupt control/status, semaphore/NVRAM/flash registers, mailbox registers, host command register, GPIO, and SCSI control pins. Bit constants describe reset, interrupt enable, flash enable, NVRAM serial bits, DMA config, and host command behavior.
- Mailbox constants define reset product IDs, host commands (`HC_RESET_RISC`, `HC_RELEASE_RISC`, `HC_CLR_RISC_INT`, etc.), self-test statuses, command completion statuses, asynchronous events, and mailbox commands (`MBC_INIT_REQUEST_QUEUE`, `MBC_ABORT_COMMAND`, `MBC_BUS_RESET`, `MBC_SET_TARGET_PARAMETERS`, `MBC_INIT_REQUEST_QUEUE_A64`, and others).
- `struct nvram` mirrors the 256-byte ISP1280/ISP12160 NVRAM layout. It contains controller flags, boot target/LUN selection, ISP/bus configuration, firmware feature bits, per-bus settings, per-target transfer/queue/PPR parameters, subsystem IDs, and checksum byte.
- IOCB structures include `struct cmd_entry`, `struct cont_entry`, `struct response`, `struct mrk_entry`, `struct ecmd_entry`, `cmd_a64_entry_t`/`request_t`, `struct cont_a64_entry`, target-mode entries (`elun_entry`, `modify_lun_entry`, `notify_entry`, `nack_entry`, `atio_entry`, `ctio_entry`, `ctio_ret_entry`, `ctio_a64_entry`, `ctio_a64_ret_entry`), and their entry type constants.
- Completion and status constants (`CS_COMPLETE`, `CS_DMA`, `CS_RESET`, `CS_DATA_UNDERRUN`, `CS_BAD_PAYLOAD`, `CS_RETRY`, etc.) encode firmware completion state returned in response entries.
- `struct bus_param` models cached bus configuration, while `struct qla_driver_setup` stores user/setup policy masks for sync, wide, PPR, and NVRAM behavior.
- `struct scsi_qla_host` is the main adapter state: Linux `Scsi_Host`, PCI/device identity, I/O bases, interrupt counts, outstanding SRB table, bus settings, mailbox output snapshot, DMA request/response rings and indices, done queue, mailbox wait/timer, online/reset flags, cached NVRAM, and firmware version/start metadata.

## Control Flow
The header defines the data shapes used by runtime flows:
- Initialization reads PCI registers, validates product IDs from mailboxes, loads or skips firmware based on NVRAM/controller flags, initializes request and response queues using the mailbox commands, and fills `struct scsi_qla_host` ring and firmware fields.
- SCSI I/O submission allocates or finds an `srb`, formats a `cmd_entry` or `cmd_a64_entry_t`, adds continuation entries for additional data segments, posts the request ring, and marks `SRB_SENT`.
- Interrupt/completion handling reads `struct response` entries, decodes `comp_status`, `state_flags`, residuals, and sense data, looks up the `handle` in `outstanding_cmds`, completes the matching SRB, and advances response ring indices.
- Error recovery uses mailbox commands and host commands for abort command/device/target, bus reset, RISC reset/release, and marker entries to synchronize target/LUN queues.
- Target-mode support, where used, relies on ATIO/CTIO/notify entries and option flag bits to accept initiator I/O, send target data/status, and acknowledge asynchronous target events.

## State and Persistence
- Persistent hardware configuration is represented by `struct nvram`; the checksum field and bitfield layout make this structure sensitive to packing, endianness, and byte offsets.
- Volatile runtime state lives in `struct scsi_qla_host`: request/response DMA rings, `outstanding_cmds`, mailbox snapshots, reset/online bitfields, and firmware version fields.
- Bus and target parameters are cached in `bus_settings` but originate from NVRAM and/or firmware mailbox state.
- The request and response rings are DMA-visible state shared with the ISP firmware. Ring indices and free-entry counts must remain coherent with what firmware sees.

## Dependencies and Integration Points
- Depends on Linux SCSI core types (`struct Scsi_Host`, `struct scsi_cmnd`), PCI (`struct pci_dev`), DMA address types, timers/completions/lists, I/O accessors, and little-endian integer annotations.
- Firmware-facing integration is through mailbox registers/commands and IOCB ring entries.
- Hardware integration is exact: `struct device_reg`, IOCB structures, NVRAM layout, and status constants must match the ISP1280/ISP12160 specification.

## Risks and Edge Cases
- Bitfields in `struct nvram` encode hardware image bytes; compiler layout assumptions are a portability risk if build settings or architecture expectations change.
- Queue constants cap concurrency (`MAX_OUTSTANDING_COMMANDS` 512, request entries 255, response entries 63). Incorrect handle management can corrupt `outstanding_cmds` or complete the wrong command.
- Endianness is mixed: IOCB fields use `__le16`/`__le32`, while some register and cached state fields are native. Missing conversions can break DMA-visible requests.
- Register access mode changes semantics: relaxed reads are used for memory-mapped I/O except the DMA-sync read macro.
- The header includes target-mode IOCBs marked unused in places; stale definitions may diverge from hardware behavior if re-enabled without validation.

## Test Signals
- Compile coverage for the qla1280 driver on architectures using both MMIO and port I/O configurations.
- Hardware or emulator boot showing successful mailbox self-test, firmware execution, request/response queue initialization, and NVRAM checksum validation.
- SCSI I/O tests that exercise 32-bit and 64-bit DMA IOCBs, continuation entries, sense data, residuals, queue-full, timeout, abort, and bus reset paths.
- Fault injection around response completion statuses (`CS_DMA`, `CS_RESET`, `CS_DATA_UNDERRUN`, `CS_RETRY`) and mailbox asynchronous events.
- Static checks for endian conversions, DMA mapping lifetime, ring bounds, and bitfield/structure size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla1280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Kconfig

## Purpose
This Kconfig file declares build-time feature switches for the QLogic/Broadcom qla2xxx Fibre Channel driver and its optional target-mode fabric module. It controls whether the initiator driver, target driver, and target debug support are available in a kernel build.

## Important Symbols
- `SCSI_QLA_FC` is a tristate option named "QLogic QLA2XXX Fibre Channel Support". It builds the main `qla2xxx` Fibre Channel HBA driver.
- `TCM_QLA2XXX` is a tristate target fabric module for QLogic 24xx+ target-mode HBAs.
- `TCM_QLA2XXX_DEBUG` is a bool nested under `if TCM_QLA2XXX`; it includes target-mode debug support and the SCSI command jammer.

## Dependencies and Selected Facilities
- `SCSI_QLA_FC` depends on `PCI`, `HAS_IOPORT`, `SCSI`, and `SCSI_FC_ATTRS`.
- `SCSI_QLA_FC` also has `depends on NVME_FC || !NVME_FC`, a common Kconfig pattern that permits build ordering whether NVMe FC is enabled or absent.
- `SCSI_QLA_FC` selects `FW_LOADER` because firmware images are loaded through the kernel firmware loader and selects `BTREE` for driver data structures.
- `TCM_QLA2XXX` depends on `SCSI_QLA_FC`, `TARGET_CORE`, and `LIBFC`, and selects `BTREE`.

## Control Flow and Build Integration
Kconfig has no runtime control flow, but it shapes compilation:
- Enabling `SCSI_QLA_FC` causes the Makefile to link `qla2xxx.o` from the driver object list.
- Enabling `TCM_QLA2XXX` builds `tcm_qla2xxx.o`.
- Enabling `TCM_QLA2XXX_DEBUG` changes compiled target-mode debug behavior.

## State and Persistence
- The selected values persist in the kernel `.config` and determine whether driver code is built in, modular, or absent.
- The help text documents firmware filenames (`ql2100_fw.bin`, `ql2200_fw.bin`, `ql2300_fw.bin`, `ql2322_fw.bin`, `ql2400_fw.bin`, `ql2500_fw.bin`) expected from linux-firmware. Runtime firmware caching is described as driver behavior on request, not Kconfig state.

## Integration Points
- Integrates with the SCSI core, FC transport class (`SCSI_FC_ATTRS`), PCI, firmware loader, optional NVMe FC code, target core, and libfc.
- The target option requires the initiator/base qla2xxx driver, so target mode is layered on top of the main adapter support.

## Risks and Edge Cases
- Changing dependencies can break allmodconfig or randconfig builds, especially around optional `NVME_FC`.
- Selecting `FW_LOADER` is required for firmware-backed adapters; removing it would produce runtime probe failures.
- Target mode is limited to 24xx+ hardware in the prompt text; code paths must still guard unsupported adapters at runtime.

## Test Signals
- `make olddefconfig`, `allmodconfig`, and `randconfig` coverage with `SCSI_QLA_FC=m/y/n`, `NVME_FC=m/y/n`, and `TCM_QLA2XXX=m/y/n`.
- Build logs showing `qla2xxx.o` only when `CONFIG_SCSI_QLA_FC` is enabled and `tcm_qla2xxx.o` only when `CONFIG_TCM_QLA2XXX` is enabled.
- Module load/probe tests verifying firmware loader requests match the documented firmware filenames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Makefile

## Purpose
The Makefile defines how the qla2xxx driver objects are assembled. It maps Kconfig symbols to the main qla2xxx initiator module and the optional TCM target module.

## Important Build Rules
- `qla2xxx-y` aggregates the built-in object list for the main driver: OS glue, initialization, mailbox, IOCB, ISR, generic services, debug, support, attributes, NPIV/midlayer, debugfs, BSG, newer ASIC support, target code, template, NVMe, and EDIF components.
- `obj-$(CONFIG_SCSI_QLA_FC) += qla2xxx.o` builds the main module when the initiator driver is enabled.
- `obj-$(CONFIG_TCM_QLA2XXX) += tcm_qla2xxx.o` builds the target fabric module when target-mode support is enabled.

## Control Flow and Integration
There is no runtime control flow, but object membership affects which runtime code is linked:
- `qla_attr.o` supplies sysfs and FC transport hooks.
- `qla_bsg.o` supplies BSG passthrough and vendor command handling.
- `qla_target.o` is included in the main qla2xxx object, while `tcm_qla2xxx.o` is built as the target-core fabric module when configured.
- `qla_nvme.o` and `qla_edif.o` are compiled into the main driver, with runtime and Kconfig guards deciding active behavior.

## State and Persistence
- Build state is persisted through Kbuild outputs and module artifacts. The Makefile does not create runtime state.
- Object ordering can matter for link-time symbol resolution and init/exit section layout.

## Dependencies
- Depends on symbols selected by `Kconfig`, kernel Kbuild conventions, and the source files listed in `qla2xxx-y`.
- The included objects depend on SCSI, FC transport, PCI, firmware loader, optional NVMe FC, target core hooks, debugfs, and EDIF support.

## Risks and Edge Cases
- Removing an object can silently drop a runtime interface; for example, without `qla_bsg.o`, `qla24xx_bsg_request` and timeout hooks referenced by the FC transport template would be unresolved.
- Adding code to the tree without updating this list leaves it unbuilt.
- Including target support in the main object while also building `tcm_qla2xxx.o` requires clear symbol ownership to avoid duplicate or missing exports.

## Test Signals
- `make M=drivers/scsi/qla2xxx` with `CONFIG_SCSI_QLA_FC=m` should produce `qla2xxx.ko`.
- Enabling `CONFIG_TCM_QLA2XXX=m` should also produce `tcm_qla2xxx.ko`.
- Link tests should catch missing symbols from `qla_attr.o`, `qla_bsg.o`, target, NVMe, or EDIF components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_attr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_attr.c

## Purpose
`qla_attr.c` implements qla2xxx sysfs attributes and Fibre Channel transport callbacks. It is the user-visible maintenance and introspection surface for firmware dumps, NVRAM/VPD/flash access, link and adapter attributes, port mode controls, statistics, NPIV vport lifecycle, rport loss handling, and BSG entry points.

## Important APIs, Types, and Functions
- Binary sysfs attributes:
  - `fw_dump` reads and controls raw firmware, MCTP, MPI, and P3P minidumps through `qla2x00_sysfs_read_fw_dump()` and `qla2x00_sysfs_write_fw_dump()`.
  - `nvram` reads/writes cached or live NVRAM, recomputes checksums, writes through `ha->isp_ops->write_nvram`, and triggers reset.
  - `optrom` and `optrom_ctl` implement a staged flash read/write state machine using `ha->optrom_state`, `ha->optrom_buffer`, region start, and region size.
  - `vpd`, `sfp`, `reset`, `issue_logo`, `xgmac_stats`, and `dcbx_tlv` expose VPD, SFP/I2C-like data, reset commands, ELS LOGO, CNA stats, and DCBX TLVs.
- `qla2x00_alloc_sysfs_attr()` and `qla2x00_free_sysfs_attr()` create/remove binary files based on adapter capabilities.
- Device attributes expose firmware/option ROM versions, serial/model/PCI/link state, ZIO mode/timer/threshold, beacon and LED configuration, firmware state, thermal data, diagnostics, speed controls, DIF bundle stats, port number, firmware attributes, D_Port diagnostics, and MPI firmware state.
- Initiator/target mode controls:
  - `qlini_mode_show/store()`, `ql2xexchoffld_show/store()`, `ql2xiniexchg_show/store()`, and `qla_set_ini_mode()` coordinate initiator mode, target mode, dual mode, and exchange offload counts.
- FC transport callbacks:
  - Host getters: `qla2x00_get_host_port_id()`, `qla2x00_get_host_speed()`, `qla2x00_get_host_port_type()`, `qla2x00_get_host_symbolic_name()`, `qla2x00_get_host_fabric_name()`, and `qla2x00_get_host_port_state()`.
  - Target/rport getters: `qla2x00_get_starget_node_name()`, `qla2x00_get_starget_port_name()`, and `qla2x00_get_starget_port_id()`.
  - Rport lifecycle: `qla2x00_set_rport_loss_tmo()`, `qla2x00_dev_loss_tmo_callbk()`, and `qla2x00_terminate_rport_io()`.
  - Stats: `qla2x00_get_fc_host_stats()` and `qla2x00_reset_host_stats()`.
  - NPIV lifecycle: `qla24xx_vport_create()`, `qla24xx_vport_delete()`, and `qla24xx_vport_disable()`.
  - `qla2xxx_transport_functions` and `qla2xxx_transport_vport_functions` register the callback tables, including BSG request and timeout hooks implemented in `qla_bsg.c`.
- `qla2x00_init_host_attr()` seeds FC host attributes during adapter setup.

## Control Flow
- Sysfs binary creation iterates `bin_file_entries`, filtering entries by `IS_FWI2_CAPABLE`, QLA25xx, and CNA capability before calling `sysfs_create_bin_file()`.
- Firmware dump read first checks dump reading flags, then serializes through `optrom_mutex` and selects P3P minidump, MCTP dump, MPI dump, or standard firmware dump buffers.
- Firmware dump writes interpret numeric commands to clear/read/allocate dumps, trigger system errors or resets, issue MPI dumps, or mark ISP abort needed.
- NVRAM writes require admin capability, exact size, offset zero, and a write op. The code recomputes checksum, waits for HBA online, writes/refreshes NVRAM under `optrom_mutex`, sets `ISP_ABORT_NEEDED`, wakes DPC, and waits for chip reset.
- Flash access through `optrom_ctl` uses commands: cancel/free, stage read, stage write, and commit write. Region validation differs by adapter family and older boards are more restricted.
- Reset writes decode magic command values for ISP reset, MPI reset, FCoE context reset, IDC reset disable/enable, and flash-version cache refresh.
- Port speed writes validate 27xx/28xx support, parse requested speed, set `ha->set_data_rate`, and call `qla2x00_set_data_rate()` if the chip is up and the setting changed.
- `qla_set_ini_mode()` is a state machine over current mode and requested mode. It decides between accepting a mode change, only updating cached values, rejecting while target mode is active, or no-op; accepted changes can call `qlt_set_mode()`, mark online, and set `ISP_ABORT_NEEDED`.
- FC transport rport timeout clears stale rport pointers under host lock when the rport did not reappear, marks dead fcports, and cooperates with PCI EEH and ISP abort state.
- NPIV vport create sanity-checks the request, creates a virtual host, initializes loop/vport state, sets DIF/DIX capabilities, adds the SCSI host, initializes FC attributes, creates target state, optionally creates a QoS queue pair, and assigns a request queue. Delete reverses these resources, waits for session deletion, removes NVMe/EDIF/target/SCSI/FC state, releases IDs and queue pairs, and drops the host reference.

## State and Persistence
- Persistent hardware data: NVRAM, VPD, option ROM/flash regions, SFP/FRU fields, firmware images, and LED configuration are read or written via `ha->isp_ops` and mailbox helpers.
- Runtime state: dump buffers and reading flags, `optrom_state`/buffer/region metadata, DPC flags (`ISP_ABORT_NEEDED`, `FCOE_CTX_RESET_NEEDED`), loop state, link speed, ZIO mode/timer/threshold, beacon state, target/initiator mode fields, vport counters/maps, queue pairs, and statistics counters.
- Sysfs attribute presence is derived from runtime adapter capabilities but tied to device lifetime through alloc/free calls.
- Stats reset clears driver counters and, on FWI2-capable adapters, requests firmware statistics reset.

## Dependencies and Integration Points
- Integrates with Linux sysfs, SCSI host attributes, FC transport class, NPIV vports, rports, PCI EEH, DMA allocation, mutex/spinlock primitives, and capability checks.
- Calls many hardware operation hooks through `ha->isp_ops`: flash/NVRAM read/write, firmware version, beacon, MPI dump, PCI info, and data-rate operations.
- Coordinates with target mode (`qla_target.h`, `qlt_*`), NVMe FC (`nvme_fc_set_remoteport_devloss()` when enabled), EDIF, debug logging, DPC worker flags, and BSG callbacks from `qla_bsg.c`.

## Risks and Edge Cases
- Many write paths expose powerful maintenance operations to sysfs; capability checks and exact-size/offline checks are critical.
- Flash/NVRAM writes can trigger resets and alter persistent adapter state. Partial region validation or wrong offsets can damage firmware images.
- `optrom_state` must remain synchronized under `optrom_mutex`; failures must reset state and free buffers to avoid stuck flash sessions.
- Several sysfs functions return `0` instead of negative errors for permission or chip-down cases, which can make user-space diagnostics ambiguous.
- Rport callbacks race with rediscovery, aborts, PCI EEH, and session deletion; stale pointer clearing is protected but depends on correct `dd_data`.
- Vport create/delete spans many subsystems. Failure unwinding must release allocated IDs, SCSI hosts, DMA buffers, timers, queue pairs, and target/NVMe/EDIF resources.
- `qla2x00_reset_host_stats()` uses `sizeof(qpair->counters)` while clearing `ha->base_qpair->counters`; this relies on type compatibility and is worth static-review attention.

## Test Signals
- Sysfs smoke tests for presence/absence of attributes across adapter families and capability bits.
- Permission and offset/size tests for `nvram`, `vpd`, `sfp`, `optrom`, and dump attributes.
- Flash/NVRAM update tests with injected allocation failure, chip-down state, PCI offline state, and HBA-online timeout.
- Reset and speed-setting tests verifying DPC flags, request blocking/unblocking, and chip reset wait behavior.
- FC transport tests for host attribute values, rport dev loss timeout propagation to NVMe remote ports, LIP, stats retrieval/reset, and rport termination during rediscovery or EEH.
- NPIV create/delete stress tests including disabled vports, QoS queue pair creation, DIF/DIX capability setup, target-mode integration, and failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_attr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.c

## Purpose
`qla_bsg.c` implements the qla2xxx Fibre Channel BSG request path. It handles standard ELS and CT passthrough plus a broad vendor-specific ABI for loopback diagnostics, flash access, 84xx management, FCP priority, IIDMA, FRU/I2C/SFP operations, bidirectional diagnostic I/O, FX00 management IOCBs, SERDES access, flash update capabilities, BBCR data, private statistics, D_Port diagnostics, EDIF management, host/tgt stats, host-port management, mailbox passthrough, timeout handling, and QLA28xx image validation.

## Important APIs and Functions
- Common completion/freeing:
  - `qla2x00_bsg_job_done()` writes the BSG result, completes the `bsg_job`, releases the SRB kref, and completes optional waiters.
  - `qla2x00_bsg_sp_free()` unmaps request/reply DMA or frees remap pool buffers, schedules dummy `fcport` freeing for CT/ELS/FX IOCBs, and releases the SRB.
- ELS/CT passthrough:
  - `qla2x00_process_els()` handles `FC_BSG_RPT_ELS` and `FC_BSG_HST_ELS_NOLOGIN`, including EDIF auth ELS dispatch, dummy fcport allocation for host ELS, DMA mapping, SRB setup, and `qla2x00_start_sp()`.
  - `qla2x00_process_ct()` handles host CT requests to SNS or management server loop IDs, allocates a dummy fcport, calculates IOCB count with `qla24xx_calc_ct_iocbs()`, and starts an SRB.
- Vendor command handlers include `qla2x00_process_loopback()`, `qla84xx_reset()`, `qla84xx_updatefw()`, `qla84xx_mgmt_cmd()`, `qla24xx_iidma()`, `qla24xx_proc_fcp_prio_cfg_cmd()`, `qla2x00_read_optrom()`, `qla2x00_update_optrom()`, FRU/I2C helpers, `qla24xx_process_bidir_cmd()`, `qlafx00_mgmt_cmd()`, SERDES handlers, flash capability handlers, BBCR/stats/D_Port handlers, host/tgt stats handlers, host-port management, and mailbox passthrough.
- Dispatch:
  - `qla2x00_process_vendor_specific()` switches on `vendor_cmd[0]`.
  - `qla24xx_bsg_request()` is the FC transport entry point and switches on BSG message code.
  - `qla24xx_bsg_timeout()` searches outstanding BSG SRBs and aborts timed-out jobs.

## Control Flow
- `qla24xx_bsg_request()` initializes reply length, resolves `vha` from rport or host, rejects isolated/down/removing adapters except selected host management/stat commands, then dispatches ELS, CT, or vendor requests.
- Asynchronous ELS/CT/FX/bidirectional requests allocate an SRB, set `sp->u.bsg_job`, `sp->free`, and `sp->done`, then rely on firmware interrupt completion to call `qla2x00_bsg_job_done()`.
- Synchronous vendor commands generally copy request SG payloads into kernel or DMA buffers, issue mailbox/IOCB/helper operations, copy response data back to reply SG payloads, set vendor status in `vendor_rsp[0]`, and call `bsg_job_done()`.
- Loopback processing maps request/reply SGs, allocates coherent request/reply buffers, chooses echo versus loopback based on topology/options/payload, manipulates 81xx/8031/8044 loopback port configuration when needed, runs mailbox diagnostics, restores port config, and returns mailbox response plus command-sent type in the BSG reply area.
- Flash read/update uses `qla2x00_optrom_setup()` under `ha->optrom_mutex` to validate region and state, allocate `ha->optrom_buffer`, perform read/write through `ha->isp_ops`, copy SG data, free the buffer, and reset state.
- Bidirectional diagnostic I/O validates adapter capability, reset state, online state, cable/topology/P2P mode, performs self-login under `selflogin_lock` when needed, maps SGs, validates equal request/reply lengths, allocates an SRB, and starts a bidirectional IOCB.
- Timeout handling logs the timed-out job, detects PCI/register disconnect, searches base and additional qpairs for matching BSG SRBs, attempts firmware abort, waits up to a R_A_TOV-derived timeout, and if needed detaches the outstanding command and completes the BSG with `-ENXIO`.
- QLA28xx image validation checks adapter and physical function, locks `optrom_mutex`, verifies MPI firmware state bits, takes the FAC semaphore, calls `qla_mpipt_validate_fw()`, releases the semaphore, and reports image/config validation vendor status.

## State and Persistence
- Persistent operations include flash/option ROM update, FRU version/status writes, I2C/SFP writes, 84xx firmware update, flash image validation, and mailbox passthrough that may alter firmware state.
- Runtime state includes SRBs in outstanding queues, DMA mappings, dummy `fcport` structures, `ha->optrom_state` and buffer fields, FCP priority config (`ha->fcp_prio_cfg`, `fcp_prio_enabled`), self-login loop ID, D_Port diagnostic status/data, stats counters, and host-port enable/disable state.
- Vendor command results are often encoded in `bsg_reply->reply_data.vendor_reply.vendor_rsp[0]` using `EXT_STATUS_*`, while transport result is frequently `DID_OK << 16` even for vendor-level failures.

## Dependencies and Integration Points
- Integrates with Linux BSG (`struct bsg_job`, `bsg_job_done()`), FC BSG request/reply formats, SCSI host/rport lookup, scatter-gather DMA mapping, DMA pools/coherent buffers, mempools, workqueues, completions, mutexes, and qpair locking.
- Calls qla mailbox/firmware helpers from the wider driver: ELS/CT IOCB start, loopback/echo tests, 84xx access chip/verify chip IOCBs, NVRAM/flash ops, SFP/I2C ops, D_Port diagnostics, stats helpers, port enable/disable, EDIF app management, mailbox passthrough, and MPI flash validation.
- Tied to FC transport through `qla2xxx_transport_functions` and `qla2xxx_transport_vport_functions` in `qla_attr.c`.
- ABI definitions are shared with `qla_bsg.h` and `qla_edif_bsg.h`.

## Risks and Edge Cases
- BSG is a privileged low-level ABI; malformed payload sizes, SG counts, or vendor structs can lead to incorrect hardware operations if not validated.
- Many handlers assume exact payload struct sizes but some copy fixed `DMA_POOL_SIZE` or struct sizes from SG without checking the job payload length first. This is a review hotspot for short-buffer behavior.
- DMA mapping paths must unmap only what was mapped. The ELS/CT and FX paths have several failure labels where request and reply mapping state matters.
- Some handlers return `0` while reporting vendor-level failure in `vendor_rsp[0]`; user-space must inspect both transport and vendor status.
- Timeout handling races with firmware completion; it rechecks the outstanding slot under lock before detaching, but SRB lifetime depends on krefs and completion ordering.
- Flash and mailbox passthrough commands can alter persistent adapter state, require adapter-family checks, and may conflict with concurrent sysfs flash paths through shared `optrom_state`.
- `qla2xxx_find_rport()` dereferences `fcport->rport` while iterating; missing rport guards would be risky if list entries without rports are possible.
- QLA28xx validation returns `QLA_SUCCESS` even after setting vendor error status, so callers must rely on vendor status.

## Test Signals
- BSG ABI tests for each supported message code and vendor command, including unsupported adapter families and isolated/down/removing adapter states.
- SG mapping tests with zero SGs, multiple SGs where forbidden, short request/reply payloads, oversized flash regions, and DMA mapping failures.
- ELS and CT passthrough tests for rport and host no-login modes, including EDIF auth ELS dispatch.
- Loopback/echo diagnostics on supported topologies with forced DCBX timeout, loopback already active, mailbox reset errors, and port config restore failure.
- Flash read/update tests sharing state with sysfs optrom, including invalid region, PCI offline, allocation failure, and write failure.
- Timeout tests where firmware completes before abort, abort succeeds after delay, abort fails, and PCI EEH is active.
- Stats and host/tgt management tests checking both transport result and `EXT_STATUS_*` vendor response values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.h

## Purpose
`qla_bsg.h` defines the qla2xxx vendor-specific BSG ABI: command opcodes, vendor status codes, loopback constants, 84xx management payloads, destination addressing structures, mailbox passthrough layout, FRU/I2C/SERDES structs, flash update and BBCR data structures, D_Port diagnostic layouts, active flash image status, and driver attribute bits.

## Important APIs, Types, and Constants
- Vendor command opcodes include `QL_VND_LOOPBACK`, `QL_VND_A84_RESET`, `QL_VND_A84_UPDATE_FW`, `QL_VND_A84_MGMT_CMD`, `QL_VND_IIDMA`, `QL_VND_FCP_PRIO_CFG_CMD`, flash read/update, FRU status/version operations, I2C read/write, FX00 management, SERDES operations, flash update capabilities, BBCR, private stats, D_Port diagnostics, EDIF management, driver attributes, host/tgt stats, host-port management, mailbox passthrough, and image-set validation.
- Vendor status constants include `EXT_STATUS_OK`, generic errors, busy, invalid parameter, overrun/underrun, mailbox error, buffer-too-small, no-memory, offline, unsupported, invalid config, DMA error, timeout, data compare failure, D_Port diagnostic states, and image validation/config errors.
- Loopback constants define command-sent values, internal/external loopback options, loopback masks, ELS payload sizing, and ELS opcode byte.
- 84xx structures:
  - `struct qla84_mgmt_param`, `struct qla84_msg_mgmt`, and `struct qla_bsg_a84_mgmt` model memory read/write, config changes, and info requests.
- Addressing and IIDMA structures:
  - `struct qla_scsi_addr`, `struct qla_ext_dest_addr`, and `struct qla_port_param`.
- Mailbox passthrough:
  - `struct qla_mbx_passthru` carries 32 input and 32 output mailbox words plus reserved fields.
- FRU/SFP/I2C:
  - `struct qla_field_address`, `struct qla_field_info`, `struct qla_image_version`, `struct qla_image_version_list`, `struct qla_status_reg`, and `struct qla_i2c_access`.
- SERDES and flash:
  - `struct qla_serdes_reg`, `struct qla_serdes_reg_ex`, and `struct qla_flash_update_caps`.
- BBCR and D_Port:
  - `struct qla_bbcr_data`, `struct qla_dport_diag`, and `struct qla_dport_diag_v2`.
- Image/driver attributes:
  - `struct qla_active_regions` reports active flash image regions.
  - `struct qla_drv_attr` exposes driver capability bits such as `QLA_IMG_SET_VALID_SUPPORT`.
- The header includes `qla_edif_bsg.h`, extending the ABI for EDIF management.

## Control Flow
The header itself has no executable control flow. In `qla_bsg.c`, `vendor_cmd[0]` is matched against the `QL_VND_*` opcodes, and request/reply SG payloads are interpreted using the packed structures defined here. Vendor status constants are written to `bsg_reply->reply_data.vendor_reply.vendor_rsp[0]`.

## State and Persistence
- Structures describe both transient requests and persistent hardware state changes. Flash, FRU, I2C/SFP, mailbox passthrough, SERDES writes, and image validation commands can change adapter firmware or nonvolatile fields.
- Flexible array payloads (`qla84_msg_mgmt.payload[]`, `qla_image_version_list.version[]`) depend on caller-provided BSG payload length.
- Packed structs define ABI layout and must remain stable for user-space tools.

## Dependencies and Integration Points
- Used by `qla_bsg.c` and user-space BSG tooling that speaks the qla2xxx vendor ABI.
- Depends on fixed-width kernel integer types, packing attributes, bit macros, and EDIF definitions in `qla_edif_bsg.h`.
- Integrates indirectly with mailbox firmware, flash update logic, diagnostics, stats, target/initiator controls, and EDIF management.

## Risks and Edge Cases
- ABI stability is critical: changing opcode values, struct packing, field order, or sizes can break existing management tools.
- Several structs contain reserved fields that likely must remain zeroed or ignored for forward compatibility.
- Flexible array and length-bearing structs require strict length validation in the C handlers; otherwise short or oversized BSG payloads may be mishandled.
- Endianness is not annotated in the ABI structs, so user-space/kernel agreement on field byte order must be documented and consistently handled.
- `qla_i2c_access.buffer` is fixed at 0x40 bytes; handlers must reject or clamp larger lengths to avoid copying beyond the embedded buffer.

## Test Signals
- ABI size/layout checks for all packed structs used by user-space.
- BSG command tests that verify each `QL_VND_*` opcode dispatches to the expected handler and returns documented `EXT_STATUS_*` values.
- Fuzz or negative tests for flexible-array counts, I2C lengths, mailbox passthrough payload size, D_Port v2 payload size, and unknown opcodes.
- Compatibility tests with existing qla2xxx management utilities, especially for flash, FRU, D_Port, stats, mailbox passthrough, and EDIF commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_bsg.h -->
