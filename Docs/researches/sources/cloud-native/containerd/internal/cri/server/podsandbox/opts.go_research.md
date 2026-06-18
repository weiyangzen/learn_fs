# sources/cloud-native/containerd/internal/cri/server/podsandbox/opts.go

## Purpose

This file defines a containerd task delete option that emits the legacy NRI sandbox delete notification before deleting a sandbox task.

## Important APIs, Types, and Functions

`WithNRISandboxDelete` returns a `containerd.ProcessDeleteOpts` closure. It type-checks the process as a `containerd.Task`, constructs an NRI client, builds an `nri.Sandbox` with the sandbox ID, and invokes the NRI `Delete` event for the task.

## Control Flow

If the process is not a task, NRI client creation fails, no NRI client is configured, or the NRI invocation fails, the closure logs and returns nil so task deletion continues.

## State and Persistence Behavior

No local state is persisted. It can trigger external NRI plugin side effects during task deletion.

## Dependencies and Integration Points

It integrates with containerd process delete options, NRI v0.1 APIs, task deletion in start cleanup and exit handling, and controller shutdown.

## Risks and Test Signals

The hook intentionally suppresses NRI errors, which protects cleanup but can hide plugin notification failures. Lifecycle tests that delete sandbox tasks are the main integration signal.
