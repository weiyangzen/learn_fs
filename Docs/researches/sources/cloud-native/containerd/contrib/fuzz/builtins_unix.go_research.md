<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_unix.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins_unix.go

## Purpose
Unix-specific fuzz build imports/registrations shared by non-Windows platforms.

## Important APIs, Types, And Functions
Build-tag selected package glue.

## Control Flow
Links Unix-only components into fuzz binaries.

## State And Persistence
No direct persistence.

## Dependencies And Integration Points
Unix build constraints and containerd plugin side effects.

## Risks And Test Signals
Platform-specific initialization can drift; build is the main signal. Source size reviewed: 25 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_unix.go -->
