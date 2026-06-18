<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_test.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor_test.go

## Purpose
Unit test coverage for dumping/loading default AppArmor profile content.

## Important APIs, Types, And Functions
Defines `TestDumpDefaultProfile`.

## Control Flow
Exercises template generation and validates non-empty/default behavior.

## State And Persistence
Test-scoped output only.

## Dependencies And Integration Points
Go testing and local template helpers.

## Risks And Test Signals
Does not prove kernel-level profile load; covers template generation path. Source size reviewed: 36 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_test.go -->
