# Research: sources/cloud-native/moby/daemon/cluster/utils.go

## sources/cloud-native/moby/daemon/cluster/utils.go

Purpose: provides small shared utilities for filter conversion, swarm persistent-state I/O, state cleanup, and manager quorum calculations.

Important APIs: `convertKVStringsToMap`, `loadPersistentState`, `savePersistentState`, `clearPersistentState`, `removingManagerCausesLossOfQuorum`, and `isLastManager`. Persistent state loading reads the swarm state file, verifies the swarm node certificate exists, clears stale state if the certificate is missing, and unmarshals `nodeStartConfig`. Saving marshals config JSON and writes atomically with mode `0600`. Clearing removes all entries under the swarm state root while preserving the root directory inode.

Dependencies include JSON, filesystem operations, `atomicwriter`, and `nodeStartConfig`. Integration points are node runner start/restart, swarm init/join/leave/unlock, and filter-building code. Risks include destructive state cleanup, stale state when certificate checks fail, ignoring errors from some callers, labels without `=` becoming empty-value filters, and quorum helper off-by-one sensitivity. Tests are indirect.
