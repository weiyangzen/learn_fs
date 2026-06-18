# sources/cloud-native/containerd/integration/failpoint/cmd/cni-bridge-fp/main_linux.go

## Purpose

This Linux CNI plugin wrapper delegates to the standard `bridge` plugin while injecting configurable failpoints for `ADD`, `CHECK`, and `DEL`. It lets integration tests simulate CNI command failures or delays using pod annotations.

## Important APIs, Types, And Functions

- `netConf`, `inheritedPodAnnotations`, and `failpointConf` model CNI stdin config and external failpoint state.
- `main` registers CNI `cmdAdd`, `cmdCheck`, and `cmdDel`.
- `handleFailpoint` extracts `failpoint.cni.containerd.io/confpath` and evaluates command-specific failpoints.
- `failpointControl.delegatedEvalFn` parses and advances failpoint state.
- `updateTx` locks, reads, updates, marshals, and atomically writes the failpoint JSON file.

## Control Flow

Each CNI command first calls `handleFailpoint`. If no absolute config path annotation exists, it proceeds normally. Otherwise it opens the config under `flock`, unmarshals command failpoint strings, constructs a `failpoint.Failpoint`, stores the delegated evaluation function, updates the serialized failpoint state, and evaluates the function. If it succeeds, the wrapper delegates to `bridge` using CNI `invoke` APIs and prints the result for `ADD`.

## State And Persistence Behavior

Failpoint progression is persisted in the JSON file named by pod annotation. `continuity.AtomicWriteFile` makes updates atomic while `flock` serializes concurrent CNI invocations.

## Dependencies And Integration Points

It integrates CNI skel/invoke/version packages, containerd internal failpoint parsing/evaluation, pod annotation inheritance, Unix file locking, and the standard `bridge` CNI plugin.

## Risks And Edge Cases

The config path must be absolute and writable. Invalid JSON or failpoint syntax fails the CNI command. Delegation assumes a `bridge` plugin is installed and discoverable. The file mode `0666` relies on process umask and directory permissions for safety.

## Test Signals

This binary is exercised indirectly by failpoint-backed integration tests that need deterministic CNI command behavior.
