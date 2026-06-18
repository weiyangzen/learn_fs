# sources/cloud-native/moby/daemon/archive_tarcopyoptions.go

## Purpose
Provides the default tar extraction options used by container archive copy operations.

## APIs, Types, And Functions
`Daemon.defaultTarCopyOptions` returns an `archive.TarOptions` configured from `allowOverwriteDirWithFile`, primarily controlling `NoOverwriteDirNonDir`.

## Control Flow, State, And Integration
The function creates option structs and persists no state. It is called by extraction paths when user/group ownership copying is not requested or as a base behavior.

## Risks And Test Signals
Risks include changing overwrite semantics and accidentally allowing directory/file replacement in unsafe cases. Integration is with `ContainerExtractToDir` and `go-archive` untar behavior.
