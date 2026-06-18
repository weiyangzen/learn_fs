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
