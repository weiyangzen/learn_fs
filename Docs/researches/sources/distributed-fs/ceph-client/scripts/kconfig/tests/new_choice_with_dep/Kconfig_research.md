# sources/distributed-fs/ceph-client/scripts/kconfig/tests/new_choice_with_dep/Kconfig

## Purpose
This fixture tests prompting for newly visible choice values when dependencies are introduced.

## Important APIs, Types, and Functions
It defines `A`, a choice depending on `A` with `CHOICE_B` and new `CHOICE_C`, plus an independent choice with `CHOICE_D`, `CHOICE_E`, and `CHOICE_F` depending on `A`.

## Control Flow
Starting from an existing config, `oldconfig` receives input enabling `A`; newly visible choice members should be recognized as new and prompt appropriately.

## State and Persistence
The paired `config` file provides initial choice selections.

## Dependencies and Integration Points
Targets oldconfig prompting, choice visibility, and `sym_has_value()` behavior.

## Risks and Edge Cases
Choice members can become newly visible due to parent or member dependencies, which historically caused missed prompts.

## Test Signals
The paired test expects `oldconfig('config', 'y')` success and expected stdout prompts.
