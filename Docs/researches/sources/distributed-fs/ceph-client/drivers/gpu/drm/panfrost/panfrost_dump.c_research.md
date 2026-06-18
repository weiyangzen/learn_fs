# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_dump.c

## Purpose
This file creates Panfrost GPU devcoredumps when a job times out. It captures selected registers, active BO contents, physical page maps, and a trailer in the Panfrost dump format.

## Important APIs, Types, and Functions
The public entry point is `panfrost_core_dump`. Internal helpers are `panfrost_core_dump_header` and `panfrost_core_dump_registers`. `struct panfrost_dump_iterator` tracks headers and data offsets. The module parameter `dump_core` arms or disables one-shot dumping.

## Control Flow
On timeout, the job manager calls `panfrost_core_dump`. The function checks and clears the one-shot flag, computes file size from register dump, headers, job BO sizes, and optional BO page map, allocates vmalloc memory, fills the register header with job and GPU metadata, dumps registers adjusted for the job slot and address space, optionally builds a BO physical map, vmaps each BO, copies its contents, emits headers, appends a trailer, and hands the buffer to `dev_coredumpv`.

## State and Persistence Behavior
The only persistent local state is the module parameter. Dump contents are transient until accepted by devcoredump infrastructure. It reads job mappings, BO sg tables, GPU registers, and MMU/job slot state but does not mutate BO contents.

## Dependencies and Integration Points
It depends on Panfrost job, GEM, registers, and device state, DRM/Panfrost dump UAPI structures, `drm_gem_vmap`, sg page iteration, vmalloc, and Linux devcoredump.

## Risks
Dump size scales with BO size and may fail allocation. Missing sg tables or vmap failures mark BO dump entries invalid. It assumes PAGE_SIZE alignment for BOs. Dumping BO contents can expose user GPU memory to privileged devcoredump readers, so access policy matters.

## Test Signals
Induce GPU scheduler timeouts, verify one-shot dump behavior and manual rearm, decode with pandecode, test large BO allocation failure, BO vmap failure, and register slot/address-space offsets.
