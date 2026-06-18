# sources/compression/zlib/contrib/minizip/skipset.h

## Purpose
`skipset.h` is a header-generated skiplist set implementation used by MiniZip to track central-directory file names for `zipAlreadyThere()`. The including translation unit supplies key type, comparison, and cleanup macros.

## Important APIs, Types, and Functions
- Required application definitions: `set_key_t`, `set_cmp(a,b)`, and `set_drop(s,k)`.
- Public generated types/functions: `set_t`, `set_start()`, `set_found()`, `set_insert()`, `set_end()`, `set_ok()`, plus optional `set_alloc()`, `set_free()`, and `set_rand()`.
- Internal types include `set_node_t` and `set_rand_t`.
- Uses a compact PCG32 RNG (`set_seed()`, `set_uniq()`, `set_rand()`) to choose skiplist node heights.

## Control Flow
The application initializes `set.env` with `setjmp()`, then calls `set_start()`. Searches walk from the current maximum depth down to level zero, storing predecessor links in `set->path`. Insert first calls `set_found()`, randomly selects a level by consuming bits from `set->ran`, grows head/path arrays if depth increases, allocates a node, and splices it into all relevant levels. `set_end()` sweeps level zero, calls `set_drop()` for each key, frees node arrays and work nodes, and nulls pointers.

## State and Persistence
All state is in `set_t`: head/path pointers, node under construction for longjmp cleanup, maximum depth, RNG state, random bit cache, and optional allocation counters. There is no persistence outside heap allocations owned by the set and key resources released by `set_drop()`.

## Dependencies and Integration Points
Used directly by `zip.c` with `set_key_t` as `char *`, `strcmp()` comparison, and `set_free()` as the drop operation. It depends on `ints.h` for fixed-width MiniZip integer aliases and on standard allocation, `setjmp`, time, and assertions.

## Risks and Edge Cases
Allocation failure is handled by `longjmp(set->env, ENOMEM)`, so callers must set the environment before operations and clean up with `set_end()`. The include guard prevents multiple generated set specializations in one translation unit. The implementation writes an identifying byte into `head->key`, which assumes the key object storage can tolerate byte access. `set_clear()` is compiled out in this MiniZip use.

## Test Signals
The header comment includes an example test with integer keys and allocation-failure semantics. In this subset, test coverage is indirect through `zipAlreadyThere()` behavior in `zip.c`; no dedicated skiplist unit test is present.
