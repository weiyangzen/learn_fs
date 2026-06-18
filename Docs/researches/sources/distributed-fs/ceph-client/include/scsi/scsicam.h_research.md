<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsicam.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsicam.h

## Purpose
This small header declares SCSI CAM geometry helper functions used for legacy BIOS/HDIO geometry reporting and partition-table interpretation.

## Important APIs, Types, And Functions
It forward declares `struct gendisk` and declares `scsicam_bios_param()`, `scsi_partsize()`, and `scsi_bios_ptable()`. The functions derive BIOS-style heads/sectors/cylinders, inspect partition size geometry, and locate BIOS partition table data.

## Control Flow
There is no inline control flow. Implementations are called by disk/BIOS-parameter paths when userspace requests legacy geometry or when SCSI disk code needs CAM-compatible calculations.

## State And Persistence
No state is owned. Functions operate on a `gendisk`, capacity, and caller-provided geometry arrays or returned partition-table memory.

## Dependencies And Integration Points
It integrates SCSI disk code with block `gendisk` and legacy HDIO geometry expectations. It is compatibility-oriented rather than part of modern command processing.

## Risks
Legacy geometry is synthetic and can be wrong for large disks. Returned partition-table pointers need clear ownership/lifetime in implementation. Geometry calculations must avoid overflow with large `sector_t` capacities.

## Test Signals
Test geometry output for small, boundary, and large capacities; partition-table parsing with valid and invalid MBR data; and HDIO_GETGEO compatibility behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsicam.h -->
