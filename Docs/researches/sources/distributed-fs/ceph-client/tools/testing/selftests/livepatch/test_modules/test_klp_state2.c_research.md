# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_state2.c

## Purpose

`test_klp_state2.c` is the migration-capable version of the console loglevel livepatch state test. Version 2 can take over state from compatible previous patches and pass it back when needed.

## Important APIs, Types, and Functions

It uses `klp_get_state()`, `klp_get_prev_state()`, `kzalloc()`, `kfree()`, callback hooks, `struct klp_state` version 2, and `.replace = true`.

## Control Flow and State

Pre-patch allocates storage only if no previous compatible state exists. Post-patch either takes over previous `data` or saves/modifies `console_loglevel`. Pre-unpatch restores only when no previous compatible state exists, otherwise passes ownership back. Post-unpatch frees only when it owns the final state.

## Dependencies and Integration Points

It depends on livepatch cumulative state compatibility and is used by `test-state.sh` with `test_klp_state3`.

## Risks and Test Signals

Risks include double-free, lost state ownership, restoring state while another compatible patch remains, or failing to detect previous state. Signals are logs stating already allocated, taking over, passing back, keeping, restoring, and freeing in the expected scenarios.
