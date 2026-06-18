# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_perf.c

## Purpose
Implements the `debugfs` `perf` file that streams GPU busy percentage and hardware performance counters for profiling when `CONFIG_DEBUG_FS` is enabled.

## Important APIs, Types, and Functions
- `struct msm_perf_state` tracks the DRM device, open state, sample counter, read mutex, output buffer, and next sample jiffies.
- `msm_perf_debugfs_init()` creates the `perf` debugfs file once per device.
- `msm_perf_debugfs_cleanup()` destroys state.
- `perf_open()` enforces single-open, starts GPU perf counters, and initializes sampling cadence.
- `perf_read()` refills and copies text samples to userspace.
- `refill_buf()` emits a header every 32 lines and otherwise waits for the next sample, samples counters, and formats output.
- `perf_release()` stops perf counters and clears open state.

## Control Flow
Opening the file requires a GPU and `gpu->lock`, rejects concurrent opens, and calls `msm_gpu_perfcntr_start()`. Reads serialize on `read_lock`; when the local buffer is exhausted, `refill_buf()` either writes a header or waits `SAMPLE_TIME` then calls `msm_gpu_perfcntr_sample()`. Release stops sampling through `msm_gpu_perfcntr_stop()`.

## State and Persistence
Debugfs state is stored in `priv->perf`. Sampling state is per-open but the file is single-open. GPU perf counter active state is owned by `msm_gpu.c`. No persistent disk state.

## Dependencies and Integration Points
Depends on debugfs, DRM minor infrastructure, MSM GPU perf counter APIs, and userspace reading `/sys/kernel/debug/dri/<minor>/perf`. It is a diagnostic interface only and compiles out without `CONFIG_DEBUG_FS`.

## Risks
Risks include single-open serialization, read blocking/interruption behavior, PM refs held while perf counters are active, fixed 256-byte buffer sizing versus counter names/counts, and stale `priv->gpu` on teardown. The driver uses mutexes and cleanup hooks to manage state.

## Test Signals
Open/read/release `perf`, verify headers and samples, concurrent open returns `-EBUSY`, interrupted reads return restart, counters stop on close, and cleanup works after debugfs removal.
