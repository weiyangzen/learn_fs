<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_sas.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_sas.h

## Purpose

`mpi_sas.h` defines the SAS-specific MPI control ABI for SMP passthrough, SATA passthrough, SAS IO Unit control, SAS status values, and SAS device-info bitfields. It is the low-level request/reply contract used by Fusion SAS code for topology, link, SATA, SMP, and device-control operations.

## Important APIs, Types, and Definitions

- `MPI_SASSTATUS_*` values describe SAS transport completion status, including invalid frame, open/connect failures, unsupported rate/protocol, STP resources busy, IU length problems, transfer-ready/data offset errors, SDSF failures, connection failure, and initiator response timeout.
- `MPI_SAS_DEVICE_INFO_*` bits classify SAS/SATA devices: product-specific high bits, SEP, ATAPI, LSI, direct attach, SSP/STP/SMP target or initiator, SATA device/host, and device type mask for no device, end device, edge expander, and fanout expander.
- `MSG_SMP_PASSTHROUGH_REQUEST` and reply send SMP frames to a SAS address or physical port with request/response lengths, connection rate, immediate flag, and SGL.
- `MSG_SATA_PASSTHROUGH_REQUEST` and reply send a SATA command FIS to a target/bus with flags for reset, execute diagnostic, DMA queued, packet command, DMA, PIO, vendor unique, write, and read.
- `MSG_SAS_IOUNIT_CONTROL_REQUEST` and reply perform link and topology operations: clear not present, clear all persistent, PHY link/hard reset, clear PHY error log, map current, send primitive, force full discovery, transmit port select, remove device, set IOC parameter, and product-specific operations.
- Primitive flags distinguish single, triple, and redundant primitive transmission.

## Control Flow

SMP passthrough builds a request with a destination SAS address, physical port, requested connection rate, data length, and SGL; firmware returns SAS status, response length, and inline response bytes. SATA passthrough embeds a 20-byte command FIS and data SGL, then returns a status FIS, status/control register snapshot, SAS status, and transfer count. IO Unit control targets either a PHY, target/bus, device handle, SAS address, or IOC parameter depending on operation; firmware completes with IOC status/log info and echoes operation metadata.

## State and Persistence Behavior

Most operations affect runtime topology and link state: resets, primitive sends, discovery, device removal, current mapping, and error-log clearing. `CLEAR_ALL_PERSISTENT` and IOC parameter changes can affect persistent or semi-persistent firmware mapping/behavior. Passthrough requests are transient but can change device state if the embedded SATA or SMP command does so.

## Dependencies and Integration Points

The header depends on MPI base types and `SGE_SIMPLE_UNION`. It is included by `mptbase.h` and used with SAS events from `mpi_ioc.h`, SAS config pages from `mpi_cnfg.h`, and SAS log info from `mpi_log_sas.h`. `mptsas.c` consumes the device-info bit definitions for topology classification and uses SAS IO Unit control for reset/discovery/device management paths.

## Risks and Edge Cases

Passthrough commands are powerful: malformed SMP frames or SATA FISes can disrupt devices or expanders. Direction flags in SATA passthrough must match the command and SGL or DMA behavior can be wrong. Several operations use overlapping identifier fields; callers must fill the fields required by the selected operation and leave irrelevant fields harmless. Link reset, hard reset, force discovery, and remove device can race with topology event handling. Connection-rate constants in this MPI v1.5 header only list negotiated, 1.5, and 3.0 Gbit rates while event structures elsewhere include 6.0 Gbit reporting.

## Test Signals

Tests should include SMP identify/report general passthrough, invalid SMP destination handling, SATA non-data/read/write passthrough on safe commands, PHY link reset and hard reset recovery, PHY error log clearing, force full discovery, remove-device behavior, and IOC parameter setting on supported firmware. Expected signals are correct SAS status, transfer count, status FIS/register data, topology events, and no stale device handles after discovery changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_sas.h -->
