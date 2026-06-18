# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_types.h

## Purpose
`xe_lmtt_types.h` defines the shared data model and ops interface for Local Memory Translation Tables.

## Important APIs, Types, And Functions
- `LMTT_PTE_INVALID` is the zero invalid entry value.
- `struct xe_lmtt` contains the root directory pointer and selected ops table.
- `struct xe_lmtt_pt` models a page table level, its backing BO, and child pointers.
- `struct xe_lmtt_ops` abstracts variant-specific root level, entry count, entry size, shift, index, and encoding.
- Externs expose `lmtt_2l_ops` and `lmtt_ml_ops`.

## Control Flow
`xe_lmtt.c` uses these structures to select a variant and perform common recursive allocation/population/drop while delegating layout math to ops.

## State And Persistence
`struct xe_lmtt` and child PT structures persist for the PF lifetime. The header itself owns no storage.

## Dependencies And Integration Points
Depends on Linux types and forward declarations for Xe BOs. It is the contract between common LMTT manager and layout-specific source files.

## Risks
The flexible array in `struct xe_lmtt_pt` exists only when allocation used the correct entry count. Ops must remain internally consistent: wrong level counts or shifts corrupt common allocation logic.

## Test Signals
Compile-time and KUnit tests that instantiate both ops tables and validate recursive allocation assumptions against the type layout.
