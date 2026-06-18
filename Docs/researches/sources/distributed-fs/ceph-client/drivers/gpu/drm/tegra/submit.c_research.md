# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.c

## Purpose

`submit.c` implements the new Tegra DRM channel submission ioctl. It copies userspace gather command streams into DMA memory, resolves mapped GEM buffers, applies relocations, validates gathers through the engine firewall, builds host1x jobs with waits and syncpoint increments, handles syncobj fences, binds optional memory contexts or stream IDs, powers the target engine, submits to host1x, and releases job resources through host1x reference counting.

## Important APIs, Types, and Functions

- `struct gather_bo` is a small host1x BO wrapper for copied gather data. It owns coherent DMA memory, a kref, and `host1x_bo_ops` for get/put/pin/unpin/mmap.
- `alloc_copy_user_array()` safely copies bounded userspace arrays with overflow detection and a 16 KiB maximum.
- `submit_copy_gather_data()` validates `gather_data_words`, allocates DMA memory, and copies the gather words from userspace.
- `submit_process_bufs()` copies `drm_tegra_submit_buf` entries, validates flags, looks up context mappings, writes relocations into gather data, and records referenced mappings in `tegra_drm_submit_data`.
- `submit_job_add_gather()` validates gather commands, enforces max per-gather words, validates command data with `tegra_drm_fw_validate()`, and appends host1x gather entries.
- `submit_create_job()` copies submit commands, allocates `host1x_job`, attaches syncpoint state, adds gathers and waits, enforces at least one gather, and returns a job ready for pinning.
- `release_job()` is installed as the host1x job release callback. It drops memory-context and mapping refs, frees job data, and drops runtime PM autosuspend.
- `tegra_drm_ioctl_channel_submit()` is the ioctl entry point.

## Control Flow

The ioctl locks `tegra_drm_file.lock`, loads the channel context from `fpriv->contexts`, optionally waits up to 10 seconds on an input syncobj, resolves an output syncobj, copies gather data, allocates per-job tracking data, processes buffer relocations, builds a host1x job from command descriptors, pins the job for the engine device, fills stream-ID or memory-context fields, powers the engine with runtime PM, installs `job->user_data`, `job->release`, and `job->timeout`, submits through `host1x_job_submit()`, returns the syncpoint end value, and optionally replaces the output syncobj fence.

Failure paths release resources in reverse order: unpin jobs, put jobs, drop memory-context refs, put mapping refs, free job data, put gather BOs, put syncobjs, and unlock the file. Once `job_data` is attached to `job->user_data`, release ownership moves to `release_job()`.

## State and Persistence Behavior

Persistent per-file/context state lives in `uapi.c` xarrays and is only referenced here. Submission creates transient gather BOs and job data. Mapping references are incremented before relocation and held until job release so submitted jobs cannot outlive the mappings. Runtime PM is acquired before submit and released in `release_job()` via autosuspend. `args->syncpt.value` is written back with the job's end threshold, and `syncobj_out` is replaced with a host1x fence when requested.

The gather BO implements host1x BO pin/unpin around copied DMA memory, so host1x pinning can map the command buffer to the engine. Relocations mutate the private copied gather buffer, not userspace memory.

## Dependencies and Integration Points

This file depends on DRM syncobj/fence APIs, dma-mapping/scatterlist helpers, host1x job/channel/syncpoint APIs, Tegra GEM lookup and BO conversion, IOMMU stream-ID helpers, runtime PM, xarray mapping state from `uapi.c`, and firewall validation from `tegra_drm_fw_validate()`. Engine clients supply `get_streamid_offset` and `can_use_memory_ctx` callbacks.

## Risks and Edge Cases

- `submit_write_reloc()` has an explicit TODO to check `target_offset` bounds against the mapped buffer; currently it can compute an IOVA beyond `mapping->iova_end`.
- The ioctl holds the per-file mutex while copying userspace memory, waiting on syncobj input, pinning jobs, powering hardware, and submitting. That simplifies lifetime but can serialize or block unrelated channel operations for long periods.
- `dma_fence_wait_timeout()` returns zero on timeout and negative on error; this code treats any nonzero as an error, so a positive success return incorrectly enters the timeout/error path. This deserves review against kernel API semantics.
- If `host1x_fence_create()` fails for `syncobj_out`, the code still calls `drm_syncobj_replace_fence(syncobj, fence)` with an error pointer unless the helper tolerates it; this looks risky.
- User array copies are capped at 16 KiB each; large valid workloads may fail with `-E2BIG`.
- Relative waits must target the job syncpoint, but absolute waits accept any ID without checking allocation in this file.
- Error unwinding after runtime PM acquisition depends on whether `job->release` was installed; `put_memory_context` handles pre-submit setup, while `release_job()` handles post-install ownership.

## Test Signals

Tests should cover invalid context IDs, zero/overflow gather sizes, oversized user arrays, bad buffer flags, invalid mapping IDs, relocation gather offset bounds, missing syncpoint allocation, invalid command flags/types, gather overflow, firewall rejection, no-gather jobs, syncobj in/out failures, memory context support and fallback stream IDs, job pin/submit failure unwinds, and reference release after asynchronous job completion. Runtime tests should watch PM get/put balance and mapping kref balance.
