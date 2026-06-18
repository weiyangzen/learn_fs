# Research: sources/cloud-native/buildkit/executor/runcexecutor/executor.go

## Purpose
runc-backed BuildKit executor for Linux workers.

## Important APIs, Types, and Functions
`Opt`, `runcExecutor`, `forwardIO`, `procKiller`, `procHandle`, and methods/functions `New`, `Run`, `Exec`, `exitError`, process killer/handle helpers.

## Control Flow
Locates runc, prepares root, registers running state, creates network/proxy namespace, writes hosts/resolv, mounts rootfs bundle, injects proxy CA, resolves user, generates/writes OCI `config.json`, records resources, calls platform `run`/`exec`, maps exits, and releases container/network.

## State and Persistence
Executor root bundles, rootfs mounts, runc state, running map, namespaces, and optional resource samples.

## Dependencies and Integration Points
Depends on go-runc, containerd mounts/OCI, BuildKit OCI/resource/network/proxy/CDI/rootless helpers, OpenTelemetry, and gateway errors. Used by OCI workers that execute through runc directly.

## Risks and Edge Cases
Cancellation/kill semantics, mount/namespace cleanup, rootless/no-process-sandbox isolation, and resource recorder release are high-risk.

## Test Signals
Runtime integration tests are the meaningful signal.
