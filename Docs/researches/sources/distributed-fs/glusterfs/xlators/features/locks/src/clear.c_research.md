# sources/distributed-fs/glusterfs/xlators/features/locks/src/clear.c

## Purpose
Implements administrative clear-lock helpers for the locks translator. It parses clear/interrupted-lock xattr commands and removes matching POSIX byte-range locks, inode locks, or entry locks from granted and/or blocked lists.

## Important APIs, Types, and Functions
- `clrlk_get_kind()` and `clrlk_get_type()` parse textual lock kind/type values.
- `clrlk_get_lock_range()` parses optional byte-range filters into `struct gf_flock`.
- `clrlk_parse_args()` parses command xattr names of the form clear/interrupted prefix plus `.t<type>.k<kind>` and optional type-specific args.
- `clrlk_clear_posixlk()` removes matching POSIX locks and unwinds blocked locks with `EINTR`.
- `clrlk_clear_inodelk()` removes matching blocked/granted inode locks and may emit contention notifications.
- `clrlk_clear_entrylk()` removes matching blocked/granted entry locks by optional basename.
- `clrlk_clear_lks_in_all_domains()` applies inode or entry clear operations across all domains on an inode.

## Control Flow
The parser first strips either the clear-lock or interrupted-lock xattr prefix, then expects ordered keyword tokens for type and kind. POSIX clearing optionally filters by byte range and, for interrupted setlk, by client UID and pid. It removes locks while holding the inode lock, moves blocked locks to local lists, then unwinds blocked frames outside the mutex. Inode and entry clearing follow the same pattern: remove from blocked lists, unwind blocked waiters, optionally remove granted locks, then call grant/notify helpers so newly unblocked locks can proceed.

## State and Persistence
The helpers mutate in-memory lock lists stored under `pl_inode_t` and domain structs. They do not persist state directly; their effects are immediate lock table changes and blocked fop unwinds.

## Dependencies and Integration Points
Depends on `locks.h`, `common.h`, lock-specific ref/unref helpers, grant helpers (`grant_blocked_locks`, `grant_blocked_inode_locks`, `grant_blocked_entry_locks`), trace/unwind helpers, and contention notification functions. Invoked by higher-level locks translator xattr handling.

## Risks and Edge Cases
The public header declares `clrlk_get__kind` with a double underscore while the implementation defines `clrlk_get_kind`, indicating a prototype mismatch risk. `clrlk_parse_args()` allocates `strlen(cmd)` bytes then scans a string into it; exact-size allocation leaves no explicit extra byte for NUL if the scanned suffix length equals `strlen(cmd)`. Removing granted entry locks unrefs inside the mutex after list removal, so ref semantics must be correct. Optional range/basename syntax cannot include `/`, by design.

## Test Signals
Test command parsing for valid/invalid type/kind, POSIX range filters, basename filters, blocked-only/granted-only/all modes, interrupted lock filtering by client/pid, and post-clear granting of waiting locks. Compile should catch the header typo if callers use the declared name.
