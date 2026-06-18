<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.h

## Purpose

`ast_post.h` declares AST POST support primitives and the compact DRAM timing table representation consumed by generation-specific AST initialization code. It centralizes sentinel/control entries for timing-table interpreters and exposes memory-controller test helpers.

## Important APIs, Types, And Macros

- `struct ast_dramstruct`: a `{ u16 index; u32 data; }` entry used for DRAM programming tables.
- `__AST_DRAMSTRUCT_DRAM_TYPE`: hardware-field index for DRAM type.
- `__AST_DRAMSTRUCT_UDELAY` and `__AST_DRAMSTRUCT_INVALID`: pseudo-indexes for table delays and end-of-table markers.
- `AST_DRAMSTRUCT_INIT()`, `AST_DRAMSTRUCT_UDELAY()`, `AST_DRAMSTRUCT_INVALID`, and `AST_DRAMSTRUCT_IS()`: helpers for defining and decoding DRAM table entries.
- Raw DWM access prototypes, `mmc_test()`, `mmc_test_burst()`, plus default extended-register setup prototypes for AST2000 and AST2300 families.

## Control Flow

The header has no runtime control flow. Its macros define the token stream that table walkers use: hardware-index writes, explicit microsecond delays, and invalid/end sentinels.

## State And Persistence Behavior

No state is stored here. The structures and constants describe writes that persist in AST memory-controller and VGA/extended registers when interpreted by POST code.

## Dependencies And Integration Points

It includes Linux integer limits/types and forward-declares `struct ast_device`. It integrates with AST generation-specific POST files, `ast_post.c`, and DRAM timing tables that need uniform pseudo-commands.

## Risks And Edge Cases

The pseudo-index values must not collide with real hardware indexes. `AST_DRAMSTRUCT_INVALID` stores `U32_MAX` as data, so consumers should treat the index as authoritative. Table walkers must handle delay entries and sentinels before issuing hardware writes.

## Test Signals

Compile coverage across AST POST files, table-walk tests that include write/delay/end entries, and hardware POST on each generation that uses these table structures are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.h -->
