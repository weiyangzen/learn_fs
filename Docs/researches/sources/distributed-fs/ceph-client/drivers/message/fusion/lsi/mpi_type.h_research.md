<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_type.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_type.h

## Purpose

`mpi_type.h` defines the base scalar and pointer typedefs used by the LSI Fusion MPT MPI headers. It is the foundation for the firmware ABI structures in the `lsi/mpi_*.h` family.

## Important APIs, Types, and Definitions

- `MPI_POINTER` defaults to `*` but can be overridden before inclusion, preserving the historical ability to express alternate pointer models.
- Signed and unsigned 8/16/32-bit aliases are `S8`, `U8`, `S16`, `U16`, `S32`, and `U32`.
- `S64` and `U64` are structs with `Low` and `High` 32-bit words rather than native C 64-bit integer aliases. `S64.High` is signed; `U64.High` is unsigned.
- Pointer aliases include `PS8`, `PU8`, `PS16`, `PU16`, `PS32`, `PU32`, `PS64`, and `PU64`.

## Control Flow

This file has no runtime control flow. Its compile-time role is to make the rest of the MPI header set agree on field widths and pointer typedef naming. Including `mptbase.h` pulls this file in before SGE, IOC, config, init, FC, LAN, RAID, target, toolbox, and SAS headers.

## State and Persistence Behavior

No state is declared. The key persistence concern is ABI stability: all firmware message structures using these typedefs depend on the aliases continuing to map to the same sizes and signedness.

## Dependencies and Integration Points

`S32` uses `int32_t` and `U32` uses `u_int32_t`, so including code must have the relevant integer typedefs available through kernel or system headers before or during inclusion. Every sibling MPI header depends on these aliases. The split-word `U64`/`S64` layout appears in DMA addresses, SAS addresses, total block counts, and protocol IUs throughout the Fusion headers.

## Risks and Edge Cases

`U64` and `S64` are not native 64-bit scalar types; code must not assume normal integer arithmetic, alignment, format printing, or endian helpers work directly on them. The low/high word order is part of the firmware ABI. `MPI_POINTER` override support is legacy and can make typedef declarations unusual if redefined. `u_int32_t` is less standard than `uint32_t` outside the kernel/BSD style environment, so portability depends on the existing include stack.

## Test Signals

Compile-time tests should assert sizes and offsets for representative MPI structures, especially fields using `U64` and `S64`. Static assertions for `sizeof(U8)==1`, `sizeof(U16)==2`, `sizeof(U32)==4`, and `sizeof(U64)==8` catch accidental include or platform drift. Build coverage should include all Fusion protocol drivers through `mptbase.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_type.h -->
