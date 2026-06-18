# Group Research: group_612_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__9f32253b8dd7

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_cnfg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_cnfg.h

## Purpose
Defines the Broadcom/LSI/Avago Fusion-MPT MPI v2.x configuration-message ABI and the associated firmware configuration page layouts used by illumos MPI-capable SCSI/SAS/PCIe adapter drivers. It maps firmware configuration actions, page headers, page-address formats, page version constants, and a large set of fixed wire-format structures for controller, manufacturing, BIOS, RAID, SAS, Ethernet, and MPI v2.6 PCIe/NVMe-related configuration pages.

## Main Interfaces
- Common config framing: `MPI2_CONFIG_PAGE_HEADER`, extended headers, page attributes/types, and extended page type constants
- Page-address encodings for RAID, SAS, enclosure, Ethernet, PCIe switch/device/link, and persistent mapping pages
- Config message ABI: `MPI2_CONFIG_REQUEST`, `MPI2_CONFIG_REPLY`, and config action constants
- Manufacturing pages 0-7 plus product-specific pages 8-31
- IO Unit and IOC pages for NVDATA, controller flags, GPIO, RAID accelerator, power/temperature, sensors, function credits, spinup, RAID capabilities, event masks, and persistent ID mapping
- BIOS pages for boot-device selection, UEFI/BIOS options, adapter order, and PHY reassignment
- RAID volume and physical disk pages for state, metadata, hot spares, paths, and disk compatibility
- SAS IO Unit, Expander, Device, PHY, Port, and Enclosure pages
- Log, RAID Configuration, Driver Persistent Mapping, Ethernet, and Extended Manufacturing pages
- MPI v2.6 PCIe IO Unit, Switch, Device, and Link pages

## Dependencies And Relationships
This header depends on the core MPI type and SGE definitions from the surrounding MPI headers, especially `mpi2.h` for base integer typedefs, `MPI2_POINTER`, `MPI2_VERSION_UNION`, and `MPI2_SGE_IO_UNION`. Several comments point consumers to `mpi2_sas.h` for SAS values and to `mpi2_pci.h` for PCIe values.

## Research Notes
The header identifies itself as `mpi2_cnfg.h` version `02.00.39`, with history through September 1, 2016. Many variable-length pages define array counts as small default macros, while comments instruct host code to leave those macros at one and use returned count or page-length fields at runtime.

## Notable Risks
- This is a firmware wire ABI; layout, padding, page versions, bit positions, and page-address encodings must match firmware exactly.
- Variable-length page arrays must be sized from returned counts or page lengths.
- MPI v2.0, v2.5, and v2.6 features coexist and must be selected according to controller support.
- Incorrect persistent config writes can alter boot order, RAID behavior, spinup policy, mappings, link configuration, discovery behavior, or enclosure state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_cnfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_hbd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_hbd.h

## Purpose
Defines the MPI v2 Host Based Discovery action request/reply ABI used by host software to add, remove, or update SAS devices in firmware-managed discovery state.

## Main Interfaces
- `MPI2_HBD_ACTION_REQUEST`
- `MPI2_HBD_ACTION_REPLY`
- HBD operations: add device, remove device, update device
- HBD device information flags for virtual, ATAPI, direct attach, SSP/STP/SMP, SATA, initiator/target roles, and device type
- HBD maximum link-rate encodings for 1.5, 3.0, 6.0, 12.0, and 22.5 Gbit/s SAS links

## Dependencies And Relationships
This header relies on MPI base typedefs and pointer macros from the MPI include stack. It complements `mpi2_cnfg.h`, whose IO Unit Page 1 includes `MPI2_IOUNITPAGE1_ENABLE_HOST_BASED_DISCOVERY`, and the core `mpi2.h` function-code space.

## Research Notes
The header identifies itself as `mpi2_hbd.h` version `02.00.04`. The request carries firmware handle, SAS address, parent handle, queue depth, PHY/port information, link rate, additional info, and arbitration wait time. The reply returns standard MPI `IOCStatus` and `IOCLogInfo`.

## Notable Risks
- HBD requests directly mutate firmware discovery topology.
- `HbdDeviceInfo` combines role/protocol bits with low-bit device type values.
- MPI v2.5/v2.6 rate values must only be used with firmware that supports those link generations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_hbd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_init.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_init.h

## Purpose
Defines MPI v2 SCSI initiator-mode request and reply message layouts for SCSI I/O, SCSI task management, and SCSI enclosure processor operations.

## Main Interfaces
- SCSI I/O payloads: `MPI2_SCSI_IO_CDB_EEDP32`, `MPI2_SCSI_IO_CDB_UNION`, `MPI2_SCSI_IO_REQUEST`, `MPI25_SCSI_IO_CDB_UNION`, `MPI25_SCSI_IO_REQUEST`
- SCSI I/O flags for sense buffer address space, SGL address/type, DMA data/DIF placement, I/O path, large CDB, bidirectional I/O, escape passthrough, EEDP, data direction, task priority, task attribute, and TLR
- SCSI I/O completion: `MPI2_SCSI_IO_REPLY`, SCSI status constants, SCSI state flags, response-info masks, and EEDP observed value flags
- SCSI task management: `MPI2_SCSI_TASK_MANAGE_REQUEST`, `MPI2_SCSI_TASK_MANAGE_REPLY`, task types, reset flags, response codes, and response-info masks
- SCSI Enclosure Processor messages: `MPI2_SEP_REQUEST`, `MPI2_SEP_REPLY`, read/write status actions, addressing flags, and slot-status bits

## Dependencies And Relationships
This header depends on core MPI definitions from `mpi2.h`, including base integer typedefs, pointer aliases, LUN field constants, MPI/IEEE SGE unions, and common IOC status/log-info handling. Configuration pages identify devices and handles; these initiator messages perform I/O, task management, and enclosure operations against them.

## Research Notes
The header identifies itself as `mpi2_init.h` version `02.00.21`, with history through January 21, 2016. It preserves separate MPI v2.0 and MPI v2.5/2.6 SCSI I/O request layouts. The SCSI I/O reply is shared for MPI v2.0 and v2.5+, with later EEDP observed fields reserved on older controllers.

## Notable Risks
- These request/reply layouts are firmware ABI; offsets, union sizes, SGL placement, and reserved fields must remain exact.
- MPI v2.0 and v2.5/2.6 SCSI I/O requests are similar but not interchangeable.
- EEDP/DIF flags and DMAFlags are dense bitfields that can alter protection-information handling.
- Task-management messages can reset links, targets, or logical units.
- SEP slot-status bits differ between requested state changes and reported enclosure state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_init.h -->