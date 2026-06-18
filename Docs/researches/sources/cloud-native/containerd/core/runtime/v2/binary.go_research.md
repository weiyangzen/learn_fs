<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/binary.go -->
# sources/cloud-native/containerd/core/runtime/v2/binary.go

## Purpose
Manages invocation of runtime v2 shim binaries for start and delete operations, including log pipe setup, bootstrap parameter persistence, connection creation, and dead-shim cleanup.

## Important APIs, Types, And Functions
- `shimBinaryConfig` holds runtime path, containerd GRPC/TTRPC addresses, socket directory, and environment.
- `shimBinary(bundle, config)` constructs a `binary`.
- `binary.Start(ctx, opts, onClose)` starts a shim with `client.Command`, streams shim logs, parses bootstrap response, connects to the shim, persists shim metadata, and returns a `shim`.
- `binary.Delete(ctx)` runs the shim delete action for a dead shim, unmarshals `task.DeleteResponse`, deletes the bundle, and returns `runtime.Exit`.

## Control Flow
`Start` builds a shim command with action `start`, opens the shim log pipe under the current namespace, starts a goroutine copying logs to stderr, runs the command and captures combined output, writes `shim-binary-path`, parses bootstrap params, creates a client connection with an on-close callback that also stops log copying, writes `bootstrap.json`, and returns a shim instance with protocol/address/version.

`Delete` logs cleanup, chooses workdir carefully by OS, builds a shim command with action `delete`, captures stdout/stderr separately, logs command failures and warnings, unmarshals the delete response, deletes the bundle directory, and maps the response to `runtime.Exit`.

## State And Persistence
Persists `shim-binary-path` and `bootstrap.json` in the bundle directory on start. Deletes the bundle during dead-shim cleanup. Holds no global state.

## Dependencies And Integration Points
Depends on runtime v2 `Bundle`, shim command package, bootstrapping helpers from `shim.go`, protobuf task API types, namespace context, logging, and runtime `Exit`. This is central to containerd daemon to shim process lifecycle.

## Risks And Edge Cases
Start must avoid leaking shim log goroutines/files on errors. `CombinedOutput` output must parse as expected bootstrap JSON/protobuf response. Delete workdir differs on Windows and FreeBSD to avoid filesystem/executable constraints. Bundle deletion after delete is irreversible and must happen only after successful shim cleanup response.

## Test Signals
No direct listed test for `binary.go`, but runtime v2 shim and manager tests elsewhere likely cover shim start/delete integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/runtime/v2/binary.go -->
