# sources/distributed-fs/ceph-client/scripts/kconfig/tests/auto_submenu/Kconfig

## Purpose
This fixture verifies automatic submenu creation when a visible symbol depends on the immediately preceding symbol.

## Important APIs, Types, and Functions
It defines `A`, dependent `A0`, dependent nested `A0_0`, sibling `A1`, a choice depending on `A1`, independent `B`, and nonconsecutive dependent `C`.

## Control Flow
When parsed and rendered by `oldaskconfig`, menu finalization should nest `A0` under `A`, `A0_0` under `A0`, and the choice under `A1`, while leaving `B` and nonconsecutive `C` at the appropriate level.

## State and Persistence
Defaults set `A` and `A0` to `y`. The fixture has no persistent state beyond generated `.config` during tests.

## Dependencies and Integration Points
It targets menu finalization and text frontend display ordering/indentation.

## Risks and Edge Cases
The key edge is that `C` depends on `A` but is not adjacent, so it must not be auto-nested merely because of dependency.

## Test Signals
The paired Python test expects `oldaskconfig()` success and stdout matching `expected_stdout`.
