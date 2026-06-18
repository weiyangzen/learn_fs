<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/daemon.go -->
# sources/cloud-native/containerd/contrib/fuzz/daemon.go

## Purpose
Shared helper for starting a containerd daemon for fuzz targets.

## Important APIs, Types, And Functions
Defines default address/root/state constants, `initDaemon`, and `startDaemon`.

## Control Flow
Creates temp-like runtime paths, launches containerd with configured address/root/state, and waits for readiness for fuzz clients.

## State And Persistence
Starts a background daemon and creates root/state directories under configured paths.

## Dependencies And Integration Points
containerd binary availability, os/exec, sync.Once, defaults.

## Risks And Test Signals
Can leave daemon/process state if fuzz process is interrupted; required by CRI/import fuzzers. Source size reviewed: 93 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/daemon.go -->
