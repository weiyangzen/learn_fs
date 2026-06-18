<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins.go -->
# sources/cloud-native/containerd/contrib/fuzz/builtins.go

## Purpose
Shared fuzz build hooks/registrations for non-platform-specific fuzz targets.

## Important APIs, Types, And Functions
Package-level initialization/import glue for fuzz builds.

## Control Flow
Compiled into fuzz package to ensure required built-in plugins or dependencies are linked.

## State And Persistence
No runtime persistence.

## Dependencies And Integration Points
Containerd plugin/import side effects.

## Risks And Test Signals
Missing imports can make fuzz harnesses fail to initialize realistic services. Source size reviewed: 52 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/builtins.go -->
