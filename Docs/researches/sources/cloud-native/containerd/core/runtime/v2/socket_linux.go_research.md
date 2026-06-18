# sources/cloud-native/containerd/core/runtime/v2/socket_linux.go

## Purpose
Defines the maximum shim socket directory length for Linux.

## APIs, Flow, State, Dependencies, Risks, And Tests
`maxSocketDirLen` is `42`, derived from Linux Unix-socket path limits after accounting for a slash and 64-character hash filename. There is no control flow or persistence.

The constant is consumed by shim manager config validation and Unix default socket directory selection. Risk is off-by-one behavior if socket naming changes. Test signals are socket path construction tests and plugin config validation for too-long `socket_dir`.
