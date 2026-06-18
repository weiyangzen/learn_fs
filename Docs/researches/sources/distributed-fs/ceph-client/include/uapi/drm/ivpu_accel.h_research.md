# sources/distributed-fs/ceph-client/include/uapi/drm/ivpu_accel.h

## Purpose

`ivpu_accel.h` defines the Intel VPU/NPU DRM accelerator ABI for device/context parameters, GEM BO creation and information, userptr BOs, command submission, explicit command queues, BO waiting, priorities, capabilities, and metric streaming. The complete 564-line header was read.

## Important APIs, Types, and Functions

The ioctl surface is `GET_PARAM`, `SET_PARAM`, `BO_CREATE`, `BO_INFO`, `SUBMIT`, `BO_WAIT`, metric streamer start/stop/get-data/get-info, `CMDQ_CREATE`, `CMDQ_DESTROY`, `CMDQ_SUBMIT`, and `BO_CREATE_FROM_USERPTR`. Core structs are `drm_ivpu_param`, `drm_ivpu_bo_create`, `drm_ivpu_bo_create_from_userptr`, `drm_ivpu_bo_info`, `drm_ivpu_submit`, `drm_ivpu_cmdq_submit`, `drm_ivpu_bo_wait`, metric streamer structs, and command queue structs.

## Control Flow

Userspace queries capabilities and context metadata, creates SHMEM or userptr BOs with returned VPU virtual addresses, submits command buffers with the first listed BO as the command buffer and the rest as referenced BOs, waits with `BO_WAIT`, and optionally uses managed command queues with priority/turbo flags. Metric collection starts a metric group, polls/probes data size or copies samples, then stops collection.

## State and Persistence Behavior

Contexts are created on open and own private VPU VA space, job queues, and an ID. BO handles persist until GEM close and carry size, flags, VPU address, and optional mmap offset. Command queue IDs persist until destroyed. Metric streamer state persists by metric group mask until stopped; stale reads can lose samples.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with the Intel VPU driver, GEM/dma-buf memory management, firmware command ABI, engine heartbeat and firmware API reporting, NPU inference runtimes, and profiling tools.

## Risks and Edge Cases

Risk centers on page alignment and lifetime of userptr BOs, unsupported cache flags, reserved fields, BO list completeness for submissions, 8-byte command offset alignment, queue ID validation, and metric buffer sizing/loss. `DRM_IVPU_BO_UNCACHED` is documented unsupported and should be rejected or redirected consistently.

## Test Signals

Cover all parameter queries, capability bits, BO flags/cache modes, userptr alignment/faults, BO info/mmap offsets, legacy and command-queue submit, priority/turbo modes, wait timeouts and aborted job status, metric start/get-info/get-data/stop including zero-size probe, and MBZ rejection.
