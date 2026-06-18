# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_atomic.c

## Purpose
Implements MSM DRM atomic check and commit tail sequencing, including asynchronous single-CRTC cursor/async updates scheduled just before vblank.

## Important APIs, types, and functions
- `msm_atomic_check()` runs MSM KMS mode-change checks and DRM atomic helper validation, with CTM changes forced through modeset.
- `msm_atomic_commit_tail()` is the main hardware commit sequence.
- `msm_atomic_init_pending_timer()` and `msm_atomic_destroy_pending_timer()` create per-CRTC FIFO kthread workers and hrtimer work.
- Helpers manage vblank refs, per-CRTC commit locks, pending mask, and async eligibility.
- Tracepoints from `msm_atomic_trace.h` instrument commit and flush phases.

## Control flow
Commit tail enables commit access, locks affected CRTC commit locks, waits for any previous flush, clears fault snapshot capture, optionally prepares the commit, pushes modeset disables, planes, and enables through DRM helpers, then either schedules async flush work or executes a synchronous flush. Async mode is allowed only for legacy cursor or async updates with no connector changes, no modeset, active state, and exactly one CRTC. The async path queues timer work one millisecond before the next vblank, immediately signals DRM commit completion, and lets the worker flush/wait/complete later under the same CRTC lock.

## State and persistence
Uses `kms->pending_crtc_mask`, `kms->commit_lock[]`, `kms->pending_timers[]`, `kms->fault_snapshot_capture`, and runtime vblank references. It does not persist state beyond current KMS runtime.

## Dependencies and integration points
Depends on `struct msm_kms` function callbacks (`enable_commit`, `prepare_commit`, `flush_commit`, `wait_flush`, `complete_commit`, `disable_commit`, `check_mode_changed`), DRM atomic helpers, DRM vblank helpers, hrtimer work, and tracepoints.

## Risks
Async completion reports hardware done to DRM before the actual flush, so ordering relies on pending masks and locks. Failure to get next vblank falls back to synchronous flush. Commit locks must be acquired/released in deterministic CRTC order to avoid deadlocks. CTM changes force modeset as a FIXME.

## Test signals
Use tracepoints for commit start/finish, flush, and wait phases. Exercise cursor async updates, multi-CRTC commits, CTM changes, vblank event timestamps, fallback when next vblank is unavailable, and suspend/destroy of pending timers.
