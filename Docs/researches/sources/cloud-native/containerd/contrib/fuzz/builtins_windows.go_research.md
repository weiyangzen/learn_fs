<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_windows.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins_windows.go

## Purpose
Windows-specific fuzz build imports/registrations.

## Important APIs, Types, And Functions
Build-tag selected package glue.

## Control Flow
Links Windows-only components for fuzz binaries.

## State And Persistence
No direct persistence.

## Dependencies And Integration Points
Windows build tags and hcsshim/containerd builtins.

## Risks And Test Signals
Coverage differs from Unix; compile/build signal only. Source size reviewed: 25 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_windows.go -->
