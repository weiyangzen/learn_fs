<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container.go -->
# sources/cloud-native/moby/daemon/container/container.go

## Purpose
Defines the core container model, durable metadata IO, checkpointing, path scoping, logging setup, restart/stdio behavior, env generation, secret/config paths, and containerd task restoration helpers.

## Important APIs, Types, And Functions
`Container`, `ExitStatus`, `SecurityOptions`, `NewBaseContainer`, `FromDisk`, `toDisk`, `CheckpointTo`, `readHostConfig`, `WriteHostConfig`, `CommitInMemory`, `SetupWorkingDirectory`, `GetResourcePath`, `GetRootResourcePath`, `StartLogger`, `StopSignal`, `StopTimeout`, `InitDNSHostConfig`, `BackfillEmptyPBs`, `RestartManager`, `InitializeStdio`, `CreateDaemonEnvironment`, `RestoreTask`, `GetRunningTask`, and `rio`.

## Control Flow
Container load reads `config.v2.json`, migrates deprecated OS into `ImagePlatform`, and reads `hostconfig.json`. Checkpointing atomically writes config and host config, creates a deep-copy snapshot, and saves it to `ViewDB`. Runtime paths are resolved through symlink-in-scope helpers. Logger startup configures driver-specific log paths, optional nonblocking ring buffer, and local read cache. Stdio connects containerd direct IO to stream pipes.

## State And Persistence Behavior
Persists `config.v2.json`, `hostconfig.json`, logs, local log cache, and root-scoped metadata paths. Runtime-only fields include RW layer, exec store, stream config, log driver, containerd handles, and attach context.

## Dependencies And Integration Points
Integrates container API types, containerd IO/tasks, logger drivers, restart manager, volume mounts, network settings, swarm secrets/configs, OCI defaults, symlink scoping, atomic writer, OTEL tracing, and errdefs.

## Risks And Test Signals
Risks include TOCTOU in scoped paths, JSON deep-copy omissions for unexported/runtime fields, log driver cache visibility, nil `HostConfig` assumptions in restart/log code, and backward-compatible port-binding mutation. Tests cover stop signal/timeout, secret targets, JSON log path, and ring logger path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container.go -->
