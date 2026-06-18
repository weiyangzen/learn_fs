# sources/cloud-native/buildkit/frontend/gateway/container/container.go

## Purpose

This file implements gateway container creation, mount preparation, process execution, lazy filesystem access, stat conversion, and cleanup. It backs `client.Container` for both in-process and gRPC gateway frontends.

## Important APIs, Types, And Functions

- `NewContainerRequest` and `Mount` are server-side container request types using `worker.WorkerRef`.
- `NewContainer` prepares mounts, creates a `gatewayContainer`, and returns it as `client.Container`.
- `setupLocalMounts` maps original mount indexes to executor mountables used by container filesystem read APIs.
- `PreparedMounts`, `MountRef`, `MountMutableRef`, and `MakeMutable` describe mount preparation outputs.
- `PrepareMounts` transforms protobuf mounts and worker refs into executor root/mount lists plus output and active refs.
- `gatewayContainer.Start`, `Release`, `ReadFile`, `ReadDir`, `StatFile`, and `mount` implement runtime behavior.
- `loadSecretEnv`, `addDefaultEnvvar`, `MountWithSession`, `mkstat`, `readlink`, and `relpath` support execution and filesystem inspection.
- `gatewayContainerProcess` implements wait, resize, and signal forwarding.

## Control Flow

`NewContainer` builds mount and ref slices, assigns `Mount.Input` indexes, calls `PrepareMounts`, records root/mounts/local mounts, and registers cleanup functions for active and output refs. On preparation error it releases any prepared refs in reverse order.

`PrepareMounts` iterates mount specs. Bind mounts may clone readonly inputs, create mutable children for outputs, or create active mutable refs for writable non-output mounts. Cache mounts come from the mount manager and may return cloned input refs as outputs. Tmpfs, secret, and SSH mounts delegate to mount manager helpers. Root mount validation requires bind mount type. Non-root mounts are made absolute relative to `cwd`, wrapped with session-aware mountables, and sorted by destination so parent paths mount first.

`Start` creates executor process metadata, adds default `PATH` and optional `TERM`, resolves secret environment variables through the session manager, and calls `executor.Run` for the first process or `executor.Exec` for later processes. `Release` cancels the container context, waits for all process errgroups, then runs cleanup LIFO. Filesystem read/stat APIs lazily mount the selected mount index and operate through `fs.FS`.

## State And Persistence Behavior

`gatewayContainer` owns mutable lifecycle state: `started`, cleanup stack, lazy `localMounts` filesystem handles, and cancellation context. Mount and ref cleanup is not persistent but is critical for cache ref and mount lifecycle. Lazy mounts are cached per mount index after first access and unmounted/closed during release. `sync.Mutex` protects start state, cleanup additions during lazy mount, and process channels.

## Dependencies And Integration Points

It integrates with BuildKit cache managers, executor, sessions, secrets, snapshot local mounters, solver mount manager, worker refs, filesystem stat types, system path helpers, and gateway client interfaces. It is used by the in-process forwarder and by the gateway gRPC server when servicing `NewContainer`/`ExecProcess` requests.

## Risks And Edge Cases

Mount lifecycle is the primary risk: every mutable ref, cloned output ref, local mounter, and opened root must be released once and in safe order. `Start` switches behavior after the first process, so concurrent first starts depend on the mutex. `ReadDir` does not apply include patterns here; container server/client paths do not pass include matching to `fs.ReadDir`, so filtering semantics differ from cacheutil-backed reference reads unless handled elsewhere. `StatFile` has a deliberate fallback for symlinks that escape an `os.Root`, returning lstat data so clients can resolve safely. Secret env optional handling appends empty values if not found and optional.

## Test Signals

No full container lifecycle tests are in this subset, but `util_test.go` covers path escape error detection used by `StatFile`. Gateway gRPC code paths exercise container creation and process I/O indirectly. More coverage would target mount preparation matrix behavior, duplicate cleanup, concurrent starts, secret env missing/optional cases, and container filesystem read/stat behavior.
