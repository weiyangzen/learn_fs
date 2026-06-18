<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker.go

## Purpose

This file implements lightweight concurrent worker-pool helpers used by nydusify to run jobs with bounded parallelism and optionally preserve ordered result delivery.

## Important APIs, Types, and Functions

`Job` is a function returning an error. `RJob` adds `Do` and `Err`. `QueueWorkerPool` has an atomic first-error store, a job channel, and per-index result channels. `NewQueueWorkerPool`, `Put`, and `Waiter` manage ordered queued jobs. `Once` is an atomic one-shot helper. `WorkerPool` provides unordered job execution with a single-error channel and waitgroup via `NewWorkerPool`, `Put`, `Err`, and `Waiter`.

## Control Flow

`QueueWorkerPool` starts workers that assign monotonically increasing result indexes under a mutex, receive jobs, run them, send the job to the matching result channel, and stop after an error. `WorkerPool` workers drain a shared queue until closed or until a job fails, with `Once` recording only the first error.

## State and Persistence Behavior

All state is in memory: channels, atomic error value, waitgroup counters, and mutex-protected index allocation. There is no persistence.

## Dependencies and Integration Points

It uses Go `sync` and `sync/atomic`. Other nydusify code can use it for parallel pulls, pushes, checks, or conversion work that needs ordered result observation.

## Risks and Test Signals

`QueueWorkerPool` has subtle ordering semantics: result index is assigned when a worker receives, not when `Put` is called, and workers stop on first job error, potentially leaving later result channels empty if callers wait blindly. `WorkerPool.Put` can block if the queue fills and no worker remains after errors. Tests cover many concurrency sizes and first-error behavior but do not run with the race detector here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker.go -->
