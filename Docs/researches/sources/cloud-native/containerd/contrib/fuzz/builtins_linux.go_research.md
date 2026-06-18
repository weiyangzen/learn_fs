<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_linux.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins_linux.go

## Purpose
Linux-specific fuzz build imports/registrations.

## Important APIs, Types, And Functions
Build-tag selected package glue.

## Control Flow
Links Linux-only snapshotter/runtime/plugin pieces needed by fuzz targets.

## State And Persistence
No direct persistence.

## Dependencies And Integration Points
Linux build tags and containerd builtins.

## Risks And Test Signals
Fuzz coverage differs by platform; compile failures expose stale imports. Source size reviewed: 27 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins_linux.go -->
