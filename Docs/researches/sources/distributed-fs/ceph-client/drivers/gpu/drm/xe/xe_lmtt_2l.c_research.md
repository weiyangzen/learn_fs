# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_2l.c

## Purpose
`xe_lmtt_2l.c` implements the two-level LMTT variant for older SR-IOV-capable platforms, mapping one root PDE per VF to a per-VF leaf table of 2 MiB local-memory PTEs.

## Important APIs, Types, And Functions
- Exports `const struct xe_lmtt_ops lmtt_2l_ops`.
- Root level is 1; leaf level is 0.
- PDE/PTE storage uses 32-bit entries.
- HAW is 37 bits with `CONFIG_DRM_XE_LMTT_2L_128GB`, otherwise 35 bits.
- Helpers provide entry counts, entry sizes, address shifts, PTE indexes, and PTE/PDE encoding with `FIELD_PREP()`.

## Control Flow
The common LMTT manager calls these ops to allocate table sizes, select indexes for guest local-memory offsets, and encode either leaf LMEM page entries or directory pointers. Leaf granularity is always 2 MiB; PDE pointers require 64 KiB alignment.

## State And Persistence
The file is stateless except for exported function-table data. Encoded PTE/PDE values persist in VRAM BOs allocated by `xe_lmtt.c`.

## Dependencies And Integration Points
It depends on bitfield/log2 helpers, Xe warning macros, and `xe_lmtt_types.h`. It is selected by `xe_lmtt.c` when the device does not require multi-level LMTT.

## Risks
Compile-time checks validate expected table sizes for configured HAW, but runtime misuse with unaligned offsets only warns and still returns encoded values. HAW configuration changes alter leaf table size and should be validated against hardware/firmware expectations.

## Test Signals
KUnit should verify HAW-dependent entry counts, 2 MiB leaf page size, 64 KiB PDE alignment checks, index wrapping, and encoding fields for representative offsets.
