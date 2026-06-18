<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/settable_test.go

## Purpose
Tests parsing and validation helpers for plugin settable options.

## Important APIs, Types, And Functions
`TestNewSettable`, `TestIsSettable`, and `TestUpdateSettingsEnv` cover `newSettable`, `isSettable`, and `updateSettingsEnv`.

## Control Flow
Parsing tests verify name/value, bare name, field syntax, empty value, and invalid leading equals. Validation tests check allowed and configured field combinations, including multiple-field ambiguity. Env tests check replace or append behavior.

## State, Dependencies, And Integration Points
No external state. It protects the lower-level parser used by `Plugin.Set` and daemon plugin setting persistence.

## Risks And Test Signals
The tests do not cover full `Plugin.Set` across mounts/devices/args, but they strongly signal syntax and env mutation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable_test.go -->
