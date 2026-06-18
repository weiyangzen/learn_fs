# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/vm_basic_types.h

## Purpose

`vm_basic_types.h` provides VMware fixed-width integer aliases, physical/page-number typedefs, common constants, byte conversion helpers, and mksGuestStats shared-memory descriptor types used by vmwgfx protocol headers.

## Important APIs, Types, and Functions

- Fixed-width aliases: `uint32`, `int32`, `uint64`, `uint16`, `int16`, `uint8`, `int8`, and `Bool`.
- Physical/page types: `PA`, `PPN`, `PPN32`, `PPN64`, and `INVALID_PPN64`.
- Limits and helpers: `MAX_UINT64`, `MAX_UINT32`, `MAX_UINT16`, `CONST64U`, `MBYTES_SHIFT`, and `MBYTES_2_BYTES`.
- mksGuestStats counters: `MKSGuestStatCounter`, `MKSGuestStatCounterTime`, flags, and aligned `MKSGuestStatInfoEntry`.
- `MKSGuestStatInstanceDescriptor`: page-based host-visible descriptor containing virtual-address starts, section lengths, arrays of pinned page numbers for stats/info/strings, and a description buffer.

## Control Flow

The header has no executable control flow. It standardizes type widths and data layout for other headers and for optional mksGuestStats communication.

## State and Persistence Behavior

The type aliases have no state. mksGuestStats descriptors and counters are persistent shared data allocated by runtime driver instrumentation code: counters are atomic64-backed, and the instance descriptor describes pinned pages that the host can walk. The comments note that the host does not acknowledge descriptor changes, so compatibility failures affect stats logging rather than core guest operation.

## Dependencies and Integration Points

- Includes Linux kernel, MM, and page headers for fixed-width kernel types, `PFN_UP`, atomics, and page sizing.
- Used by all SVGA/SVGA3D protocol headers for consistent ABI widths.
- Integrates with `CONFIG_DRM_VMWGFX_MKSSTATS` driver code that exposes guest stats to the host.

## Risks and Edge Cases

- VMware aliases must remain fixed-width; substituting C native types would make packed protocol structures architecture-dependent.
- `MBYTES_2_BYTES` name takes a count of megabytes despite the parameter name `_nbytes`; misuse can over/under-size resources.
- mksGuestStats structures contain guest virtual addresses and pinned page arrays. Runtime code must ensure pages remain pinned and lengths stay within the maximum page arrays.
- `MKSGuestStatInfoEntry` is explicitly 32-byte aligned; changing alignment affects host parsing.

## Test Signals

- Compile-time checks should verify alias sizes, `MKSGuestStatInfoEntry` alignment, and descriptor page-array capacity calculations.
- mksGuestStats tests should cover descriptor initialization, atomic counter updates, maximum stat counts, string/info section lengths, and disabled instrumentation builds.
