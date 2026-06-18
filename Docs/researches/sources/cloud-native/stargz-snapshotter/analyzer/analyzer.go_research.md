# sources/cloud-native/stargz-snapshotter/analyzer/analyzer.go

## Purpose
`analyzer.go` analyzes an image by running it under a monitored root filesystem and recording accessed paths into containerd content store as prioritized file records. The resulting digest can be used by optimization tooling.

## Important APIs, Types, and Functions
`Analyze(ctx, client, ref, opts...)` is the primary API. Helpers include `mountImage`, `waitOnSignal`, `waitOnTimeout`, `killTask`, `lazyReadCloser` with `newLazyReadCloser`, and line waiting via `newLineWaiter`, `lineWaiter`, and `registerWriter`. The file also uses analyzer options defined elsewhere, fanotify spawning, pre-container monitor service, and recorder creation.

## Control Flow, State, and Persistence
`Analyze` resolves the image, ensures it is unpacked, mounts its rootfs snapshot into a temp target, optionally records pre-container accessed paths, spawns a fanotify process in a mount namespace, builds an OCI spec with rootfs pointing at the target and mount namespace bound to fanotify, creates a container and task, starts an image recorder, starts fanotify monitoring, runs the task, waits by signal, timeout, or output line, kills the task when needed, closes fanotify, and commits the record to the content store. Persistent outputs are recorder content blobs in containerd content store and temporary snapshots cleaned by deferred functions.

## Dependencies and Integration Points
The file depends on containerd client/image/snapshot/task APIs, containerd ctr signal helpers, mount package, OCI spec helpers, errdefs/log/platforms, fanotify analyzer packages, recorder package, OCI identity, console handling, and runtime-spec. It integrates with snapshotters, content store, Linux mount namespaces, fanotify, and container lifecycle.

## Risks and Test Signals
This is privileged Linux-specific logic with many cleanup paths. Mount preparation deliberately avoids containerd preparing rootfs inside the wrong namespace. Container creation retries ID collisions three times. Terminal mode requires stdin and conflicts with wait-on-signal. `lazyReadCloser` waits for task registration before allowing stdin reads and closes task IO on EOF. Fanotify shutdown uses a mutex-protected flag to distinguish expected EOF. Risks include leaked mounts/snapshots on partial failures, races around fanotify closure, external process namespace behavior, and unbounded wait if signal/timeout configuration is wrong. Test signals likely come from integration tests and analyzer package tests outside this subset.
