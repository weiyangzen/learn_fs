# Research: sources/cloud-native/containerd/cmd/containerd/builtins/builtins_unix.go

## Purpose
Registers Unix non-Linux builtins shared across supported Unix platforms.

## Important APIs, Control Flow, And State
Blank imports register EROFS and walking diff plugins plus blockfile, EROFS, and native snapshotters. There are no functions; imported package init functions update the plugin registry.

## Dependencies And Integration
Applies through Unix build tags where Linux-specific file does not replace the needed set. It keeps daemon plugin availability aligned across Unix variants.

## Risks And Test Signals
Risks include platform build tag overlap/omission and plugin dependency portability. Platform build tests should confirm the intended imports compile and plugin graph contains expected diff/snapshotter plugins.
