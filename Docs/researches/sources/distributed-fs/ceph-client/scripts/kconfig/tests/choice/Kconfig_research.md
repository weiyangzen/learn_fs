# sources/distributed-fs/ceph-client/scripts/kconfig/tests/choice/Kconfig

## Purpose
This fixture defines a minimal boolean choice with a default member to test baseline choice semantics.

## Important APIs, Types, and Functions
The `choice` has prompt `boolean choice`, default `BOOL_CHOICE1`, and two bool members `BOOL_CHOICE0` and `BOOL_CHOICE1`.

## Control Flow
Kconfig should select the default when appropriate and emit exactly one selected choice member across oldask/allyes/allmod/allno/alldef modes.

## State and Persistence
Generated `.config` content records the selected choice symbol. The source has no external state.

## Dependencies and Integration Points
Targets choice parsing, default selection, and all*config modes in `conf`.

## Risks and Edge Cases
Module mode should not create invalid `m` values because members are boolean.

## Test Signals
The paired tests compare stdout/config against expected files for multiple config modes.
