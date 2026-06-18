# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_defs.h

## Purpose
`pm8001_defs.h` provides common compile-time limits, chip identifiers, simple protocol enums, memory-region identifiers, and status constants shared across the pm8001 driver. It is the driver-wide vocabulary for chip flavor selection, PHY speeds, data directions, port types, queue capacities, memory-map regions, MPI error returns, PHY control operations, HBA state flags, and link-state values.

## Important APIs, Types, And Constants
`enum chip_flavors` identifies supported SPC/PM80xx device families, including `chip_8001`, `chip_8008`, `chip_8009`, `chip_8018`, `chip_8019`, `chip_8074`, `chip_8076`, `chip_8077`, `chip_8006`, `chip_8070`, and `chip_8072`. Many code paths branch on `chip_8001` versus later chips to select configuration table layouts and BAR-shift behavior.

`enum phy_speed` maps firmware speed bits to 1.5, 3, 6, and 12 Gbps capabilities. `enum data_direction` maps DMA direction to firmware command bits, and `enum port_type` distinguishes SAS and SATA links in per-phy state. Capacity macros define driver limits: `PM8001_MAX_CCB` 1024, `PM8001_MPI_QUEUE` 1024 entries, up to 64 inbound and outbound queues, `PM8001_CAN_QUEUE` 508, 16 phys/ports, 2048 devices, and 64 MSI-X vectors for newer hardware. IOMB sizes are 64 bytes for SPC and 128 bytes for SPCV.

`enum memory_region_num` names DMA memory regions: AAP1 event log, IOP event log, NVMD buffer, firmware flash buffer, forensic memory, and the base count used to derive queue-memory region indices. `USI_MAX_MEMCNT` expands this base count by inbound/outbound queues plus producer/consumer index regions. `enum mpi_err` is used by queue consumption paths as success, busy, or failure. `enum phy_control_type` is the local PHY-control command vocabulary. `enum pm8001_hba_info_flags` distinguishes init-time from run-time behavior.

## Control Flow
The file has no executable control flow. It shapes control flow in C files by fixing array bounds, queue loops, state-machine comparisons, and branch conditions. For example, HWI queue initialization iterates to `pm8001_ha->max_q_num` within the maximums defined here, task scanning uses `PM8001_MAX_CCB`, fatal cleanup may scan `PM8001_MAX_DEVICES`, and completion decoding uses direction and port type values from these enums.

## State And Persistence Behavior
The definitions describe state stored elsewhere, especially `pm8001_hba_info`, per-device entries, queue tables, memory-map entries, and PHY structures. They do not persist anything by themselves. Hardware flash/NVMD persistence is represented only indirectly through memory-region and size constants.

## Dependencies And Integration Points
This header is included by pm8001 driver sources and is coupled to firmware ABI limits. It integrates with libsas by aligning PHY speed and port type concepts with SAS/SATA topology handling. It also integrates with Linux block/SCSI limits through `PM8001_MAX_IO_SIZE`, `PM8001_MAX_DMA_SG`, and `PM8001_MAX_SECTORS`.

## Risks And Edge Cases
Because these are global limits, increasing any queue, device, CCB, or DMA scatter-gather macro can change memory allocation sizes, MMIO table layout expectations, and firmware-visible queue descriptors. `PM8001_MAX_IO_SIZE` determines derived SG and sector limits, so mismatches with firmware or block-layer constraints can cause I/O mapping failures. Chip flavor additions require synchronized updates in dispatch selection, table parsing, and sysfs code; this header alone does not enforce complete support.

## Test Signals
Compile-time test signals include array bounds, switch exhaustiveness in chip dispatch, and no overflow in memory-region count calculations. Runtime signals include correct queue allocation sizes, proper SCSI queue depth, correct link-rate translation, and successful operation across chip_8001 and newer PM80xx hardware families.
