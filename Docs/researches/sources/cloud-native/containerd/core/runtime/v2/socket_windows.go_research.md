# sources/cloud-native/containerd/core/runtime/v2/socket_windows.go

## Purpose
Defines the maximum shim socket directory length for Windows builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`maxSocketDirLen` is `42`, matching the Linux-derived calculation used by shim socket path construction. The file has no control flow or persistence.

It integrates with shim manager config validation. Risks are documentation/constant drift if Windows transport naming changes. Test signals are Windows build compilation and `socket_dir` length validation.
