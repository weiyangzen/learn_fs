## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/snapshotter.go

Purpose: defines a shared snapshotter name flag.

Important APIs/types/functions: `SnapshotterFlag` and `SnapshotterFlags`.

Control flow: no direct execution; commands can read the flag, defaulting to empty or `CONTAINERD_SNAPSHOTTER`.

State and persistence: none.

Dependencies and integration: used by commands that need to pass a snapshotter name to containerd operations.

Risks and test signals: no validation and no direct tests in this subset.
