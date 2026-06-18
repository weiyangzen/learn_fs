<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_unsupported.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor_unsupported.go

## Purpose
Unsupported-platform stubs for AppArmor OCI spec options.

## Important APIs, Types, And Functions
Defines `WithProfile` and `WithDefaultProfile` returning no-op/error behavior for unsupported builds.

## Control Flow
Build-tag selected when AppArmor support is unavailable; functions prevent Linux-specific implementation from compiling into other targets.

## State And Persistence
No persistence.

## Dependencies And Integration Points
Build tags and OCI spec option type.

## Risks And Test Signals
Callers may assume profile enforcement that is unavailable on the platform; compile-time selection is the guard. Source size reviewed: 43 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor_unsupported.go -->
