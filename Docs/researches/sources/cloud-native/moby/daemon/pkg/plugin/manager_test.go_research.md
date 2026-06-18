<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_test.go

## Purpose
Tests plugin privilege validation semantics.

## Important APIs, Types, And Functions
`TestValidatePrivileges` exercises `validatePrivileges` and implicitly `normalizePrivileges` using `plugin.Privileges`.

## Control Flow
The table compares required privileges against provided privileges and expects success only when lengths, names, and value sets match. One case confirms privilege and value ordering does not matter.

## State, Dependencies, And Integration Points
No external state. This protects the install/upgrade privilege gate used by Linux plugin pull and upgrade.

## Risks And Test Signals
Descriptions are ignored by validation, while names and values are strict and case-sensitive. The test covers empty, mismatched length, mismatched values, order-insensitive success, and single-privilege behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_test.go -->
