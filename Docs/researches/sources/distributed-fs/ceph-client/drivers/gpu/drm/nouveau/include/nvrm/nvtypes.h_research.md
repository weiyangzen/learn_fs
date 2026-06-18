# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvrm/nvtypes.h

## Purpose

This header provides NVIDIA RM-compatible scalar typedefs and alignment macros used by Nouveau's generated or imported GSP/RM interface structures.

## Important APIs, Types, and Functions

Key declarations are `NV_ALIGN_BYTES`, `NV_DECLARE_ALIGNED`, `NvV32`, `NvU8`, `NvU16`, `NvU32`, `NvU64`, `NvP64`, `NvBool`, `NvHandle`, `NvLength`, `RmPhysAddr`, `NV_STATUS`, and `rpc_generic_union`.

## Control Flow

There is no executable flow. The typedefs allow RM/GSP protocol headers to express fixed-width ABI fields with names matching NVIDIA's firmware interface.

## State and Persistence Behavior

The header stores no state. It affects binary layout and ABI compatibility for structs that may be shared with firmware or RM-style RPC payloads.

## Dependencies and Integration Points

It integrates generated GSP/RM headers with Linux fixed-width integer types and compiler alignment attributes.

## Risks

Changing typedef widths or alignment macros would break firmware ABI layouts. Pointer-like `NvP64` fields must remain explicit 64-bit protocol addresses rather than native kernel pointers when used in wire structures.

## Test Signals

Compile generated RM headers, assert structure sizes/offsets for GSP RPC payloads, and boot GSP firmware that consumes aligned protocol structures.
