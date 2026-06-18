# sources/distributed-fs/ceph-client/fs/ubifs/debug.h

## Purpose
`debug.h` declares UBIFS debug state, logging/check macros, dump/check APIs, debugfs lifecycle hooks, and recovery-testing LEB wrappers. It is the interface between normal UBIFS code and the implementations in `debug.c` plus subsystem-local debug checkers.

## Important APIs, Types, and Functions
- Callback types `dbg_leaf_callback` and `dbg_znode_callback` are used by `dbg_walk_index()`.
- `struct ubifs_debug_info` stores per-mount old-index snapshots, power-cut injection state, lprops/budget snapshots, check flags, recovery-test flags, and per-mount debugfs dentries.
- `struct ubifs_global_debug_info` stores global default debug flags.
- `ubifs_assert()` and `ubifs_assert_cmt_locked()` provide UBIFS-specific assertion behavior.
- `dbg_gen()`, `dbg_jnl()`, `dbg_tnc()`, `dbg_find()`, and related macros produce typed dynamic debug messages.
- Inline flag readers such as `dbg_is_chk_gen()`, `dbg_is_chk_index()`, `dbg_is_chk_fs()`, and `dbg_is_tst_rcvry()` combine global and per-mount settings.
- The header declares all debug dump, consistency check, LEB wrapper, and debugfs lifecycle functions.

## Control Flow
Callers use cheap inline flag checks before invoking expensive debug checks. `ubifs_assert()` routes failed expressions to `ubifs_assert_failed()`, which applies runtime assertion policy. Debug message macros format messages with UBIFS category tags and current pid; key-aware variants use `dbg_snprintf_key()` into a stack buffer.

## State and Persistence Behavior
The header defines the shape of per-mount debug state allocated during mount debugging initialization and freed at unmount. Saved old index and lprops/budget values are transient validation snapshots. Power-cut fields track simulated failure progress across wrapped UBI operations during a mounted test run. No persistent media layout is defined here, but these declarations control wrappers that can affect media writes under recovery testing.

## Dependencies and Integration Points
It depends on UBIFS core types such as `struct ubifs_info`, `struct ubifs_zbranch`, `struct ubifs_znode`, lprops/budget structures, and kernel `debugfs` dentries. It is included by UBIFS source files to access assertions, debug logging, optional checks, debugfs initialization, and I/O wrappers.

## Risks and Edge Cases
- Debug flags are bitfields without locking in the inline readers; they are runtime diagnostics and tolerate simple races.
- Assertion behavior depends on `c->assert_action`; callers should not assume a failed assertion always terminates execution.
- Key debug printing macros require a visible `c` variable in scope for `dbg_snprintf_key()`.
- Per-mount debugfs directory name length is bounded by `UBIFS_DFS_DIR_LEN`; unexpected UBI numbering beyond the documented pattern causes debugfs init to skip the instance directory.

## Test Signals
Compile-time and runtime signals include building with UBIFS debug enabled, toggling global and per-mount check flags through debugfs, verifying `ubifs_assert()` policy handling, confirming debug message categories appear under dynamic debug, and checking that recovery wrappers replace raw UBI operations when recovery testing is active.
