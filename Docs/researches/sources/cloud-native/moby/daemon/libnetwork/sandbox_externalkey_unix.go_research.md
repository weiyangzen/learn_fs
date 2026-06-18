<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unix.go

Purpose: Linux/FreeBSD external network namespace key handoff for containers created by an OCI runtime.

Important APIs/types/functions: reexec registration `libnetwork-setkey`, `setKeyData`, `processSetKeyReexec`, `setKey`, `setExternalKey`, `processReturn`, controller `startExternalKeyListener`, `acceptClientConnections`, `processExternalKey`, and `stopExternalKeyListener`.

Control flow: runtime reexec reads OCI `specs.State` from stdin, derives `/proc/<pid>/ns/net`, and sends container ID/key plus OpenTelemetry trace context over a Unix socket under `<exec-root>/libnetwork/<short-controller-id>.sock`. The controller listener accepts JSON requests, finds the sandbox, calls `Sandbox.SetKey`, and returns `"success"` or an error string.

State and persistence: creates a Unix socket and stores listener on controller. The actual sandbox namespace state is updated by `SetKey`.

Dependencies and integration points: uses `reexec`, OCI runtime state, controller exec root, OpenTelemetry propagation, and Unix sockets.

Risks and test signals: socket permissions/path cleanup and partial JSON reads are sensitive. External key setup is critical for joining an already-created container netns. Tests for external key behavior exist elsewhere; this subset includes no direct test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unix.go -->
