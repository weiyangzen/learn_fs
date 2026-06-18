# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-state.sh

## Purpose

`test-state.sh` validates livepatch system-state storage and migration across cumulative livepatches. It uses console loglevel changes as the stateful side effect.

## Important APIs, Types, and Functions

It uses `load_lp()`, `load_failing_mod()`, `disable_lp()`, and modules `test_klp_state`, `test_klp_state2`, and `test_klp_state3`. The modules use `klp_state`, `klp_get_state()`, and `klp_get_prev_state()`.

## Control Flow and State

The script tests basic allocation/fix/restore/free of console loglevel state, then loads a compatible cumulative patch that takes over the existing state, unloads/reloads compatible versions, and finally attempts an incompatible version mismatch that must fail. State persists inside livepatch state records while patches are stacked.

## Dependencies and Integration Points

It depends on livepatch replace/cumulative behavior, state version compatibility, console loglevel globals, and exact callback logs.

## Risks and Test Signals

Risks include leaking state data, restoring console loglevel too early, incompatible cumulative patches loading, or compatible patches failing to take over state. Signals are exact logs for allocation, takeover, restore, free, and an `Invalid parameters` failure for incompatible versions.
