# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_windows.go

## Purpose

This Windows file builds the sandbox OCI spec for Windows pause containers and supplies Windows no-op file/snapshot hooks.

## Important APIs, Types, and Functions

`sandboxContainerSpec` sets image env, hostname, cwd, process args, clears root, sets the HCS network namespace, applies default sandbox CPU shares, chooses RunAs username, applies credential spec, forwards allowed annotations, records HostProcess annotation, and adds default CRI annotations. Other hooks return nil or empty options.

## Control Flow

Spec generation rejects images with no entrypoint or command. CRI `RunAsUsername` overrides image user. Credential spec is added only when present. File setup and cleanup are no-ops because Windows does not need the Linux sandbox files.

## State and Persistence Behavior

No files or mounts are created. State is limited to generated OCI spec fields and annotations.

## Dependencies and Integration Points

It integrates with hcsshim-facing Windows OCI fields, CRI Windows security context, default CRI annotations, and shared controller start logic.

## Risks and Test Signals

Risks include user validation being deferred to hcsshim and incomplete HostProcess/network namespace combinations. Windows tests assert network namespace, user override, credential spec, CPU shares, and annotations.
