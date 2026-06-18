# Research: sources/cloud-native/containerd/cmd/containerd-stress/exec_worker.go

## Purpose
Implements stress workers that repeatedly create a container and run an exec process inside it.

## Important APIs, Control Flow, And State
`execWorker` embeds `ctrWorker`. `exec` loops until timeout, creates a container/task using the embedded worker path, then calls `runExec` with a generated process spec, tracking counts, failures, and exec timing metrics. `runExec` creates an exec process, starts it, waits for completion, and handles cleanup with task/container deletion paths. State includes remote container/task/exec lifecycle and local counters.

## Dependencies And Integration
Uses containerd client, `cio`, OCI helpers, runtime spec process definitions, syscall signals, logging, and metrics from `main.go`. It complements normal `ctrWorker` stress to exercise exec-specific shim paths.

## Risks And Test Signals
Risks include cleanup gaps if exec creation or start fails, blocking waits after timeout, and shared counter access through the final result. Tests should cover exec success, create/start/wait failures, timeout cancellation, and cleanup ordering.
