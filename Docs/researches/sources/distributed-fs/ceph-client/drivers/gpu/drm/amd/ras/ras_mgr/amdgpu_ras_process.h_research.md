# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_process.h

## Purpose

`amdgpu_ras_process.h` declares the AMDGPU RAS event-processing interface used by the manager and interrupt dispatch paths.

## Important APIs, Types, And Functions

It forward-declares `enum ras_ih_type` and declares init/fini, UMC/unexpected/consumption interrupt handlers, process begin/end callbacks, and pre/post reset hooks.

## Control Flow, State, And Persistence

The header has no control flow. Its functions operate on manager-owned delayed work, pause flags, completion state, and rascore event queues.

## Dependencies And Integration Points

It depends on `struct amdgpu_device` and is included by `amdgpu_ras_mgr.h` and implementation files that enqueue or pause RAS work.

## Risks And Test Signals

Risks are signature drift and callers using the process API before manager init. Test signals include build coverage and null/invalid manager context tests around reset and interrupt paths.
