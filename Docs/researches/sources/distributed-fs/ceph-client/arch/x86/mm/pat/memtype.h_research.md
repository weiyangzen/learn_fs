# sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.h

## Purpose
This private PAT header defines the memory-type reservation record, debug printing, cache-mode names, and interval-tree backend prototypes or stubs.

## Important APIs, Types, and Functions
- `struct memtype` stores `[start,end)`, `subtree_max_end`, cache `type`, and rb-tree node.
- `cattr_name()` maps `enum page_cache_mode` values to human-readable strings.
- `dprintk()` emits PAT debug output only when `pat_debug_enable` is set.
- Prototypes include `memtype_check_insert()`, `memtype_erase()`, `memtype_lookup()`, and `memtype_copy_nth_element()`.
- When `CONFIG_X86_PAT` is disabled, static inline stubs provide no-op behavior.

## Control Flow and State
The header has no runtime state beyond declarations. It standardizes interval endpoint representation as exclusive `end` in `struct memtype`, while the interval backend converts to inclusive ends for the generic interval tree.

## Dependencies and Integration Points
`memtype.c` and `memtype_interval.c` include this header. Debugfs printing and conflict diagnostics rely on `cattr_name()`. The stubs allow `memtype.c` to compile when PAT tracking is disabled.

## Risks
The exclusive-end convention must remain consistent between reservation, lookup, and erase. Stubs returning success/null are correct only when higher-level PAT-disabled paths avoid relying on actual tracking.

## Test Signals
Compile both PAT-enabled and disabled configurations. Runtime debug messages should use consistent cache names, and interval-tree operations should preserve exact range endpoints.
