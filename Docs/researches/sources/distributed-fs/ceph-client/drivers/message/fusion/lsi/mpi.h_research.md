# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi.h Research

## Purpose
`mpi.h` is the base LSI Fusion MPT Message Passing Interface header. It defines product-independent MPI versioning, IOC states, PCI system-interface register offsets, doorbell fields, message function codes, scatter-gather element layouts/macros, standard request/reply headers, and IOC status/log-info constants.

## Important APIs, Types, And Functions
Version constants include `MPI_VERSION_MAJOR`, `MPI_VERSION_MINOR`, `MPI_VERSION`, and `MPI_HEADER_VERSION`. IOC state and fault macros define reset/ready/operational/fault states and PCI parity/bus fault codes. System interface macros define doorbell, write-sequence, diagnostic, interrupt, and request/reply FIFO offsets. Function codes cover SCSI I/O, task management, IOC init/facts/config, port enable, events, firmware upload/download, target mode, FC/SAS/SATA/SMP, diagnostic, LAN, inband, reset, handshake, reply-frame removal, and host page-buffer access. Types include `MPI_VERSION_STRUCT`, `MPI_VERSION_FORMAT`, multiple `SGE_*` simple/chain/transaction structures, `SGE_MPI_UNION`, `MSG_REQUEST_HEADER`, and `MSG_DEFAULT_REPLY`. SGE helper macros pack and unpack flags, lengths, chain offsets, and context reply types.

## Control Flow
The header has no executable control flow, but it defines the wire-format constants used by Fusion drivers to program request frames, parse reply frames, poll/register interrupts, post/free FIFO entries, construct SGLs, and classify controller status.

## State And Persistence
It models hardware/firmware protocol state rather than owning runtime state. Values describe persistent ABI contracts between host drivers and IOC firmware; changing them would break binary protocol compatibility.

## Dependencies And Integration Points
The header depends on base integer typedefs such as `U8`, `U16`, `U32`, `U64`, and `MPI_POINTER` provided by surrounding Fusion headers. It is included by transport-specific and common Fusion MPT drivers that implement SCSI, FC, SAS, LAN, control, and firmware operations.

## Risks
This is ABI-sensitive protocol material: structure packing, field widths, endian expectations, and numeric constants must match firmware. Some macros perform read-modify-write style assignments or rely on caller-provided lvalues. Flexible/placeholder transaction detail arrays require careful sizing. IOCStatus ranges overlap obsolete aliases and transport-specific meanings, so decoding code must mask `MPI_IOCSTATUS_FLAG_LOG_INFO_AVAILABLE`.

## Test Signals
Compile all Fusion transports against the header, run sparse/endian checks, validate request/reply sizes against firmware specs, exercise SGE construction for 32-bit and 64-bit DMA, decode representative IOCStatus/log-info values, and test reset/doorbell/interrupt paths on supported adapters or emulation.
