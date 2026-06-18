# Research: sources/cloud-native/containerd/client/task.go

## Purpose
Defines the client-side `Task` API for init process lifecycle, exec processes, metrics, resource updates, checkpointing, and OCI spec access.

## Important APIs, Control Flow, And State
The file defines process statuses, IO close info, checkpoint/task/update structs, `TaskInfo`, and the `Task` interface. `task` methods delegate to the task service for start, kill, pause/resume, status, wait, delete, exec, pids, close IO, resize, metrics, checkpoint, update, and process loading. Deletion checks stopped-like state, handles Windows-created PID 0 exceptions, cancels/waits/closes IO carefully, and converts errors. `Exec` creates IO before sending the exec request and cleans it on failure. `Checkpoint` creates a lease, optionally pauses/resumes the task, asks runtime for checkpoint descriptors, optionally includes image and RW snapshot descriptors, writes an OCI index, and creates a checkpoint image unless options dump to a direct path. Persistent state includes runtime task state, content descriptors, checkpoint image records, RW snapshot diffs, and local IO handles.

## Dependencies And Integration
Uses task service protobufs, runc options, typeurl, content/diff/images/mount/rootfs, OCI specs, `cio`, tracing, errdefs, and plugin runtime constants. It is the main client abstraction over shim task services.

## Risks And Test Signals
Risks include task deletion while still running, IO leaks, checkpoint pause/resume failures, wrong runtime option unmarshaling, metrics nil handling, and races during image create. Tests should cover lifecycle calls, exec cleanup, delete preconditions, checkpoint variants, update resource type encoding, metrics not-found handling, and process loading.
