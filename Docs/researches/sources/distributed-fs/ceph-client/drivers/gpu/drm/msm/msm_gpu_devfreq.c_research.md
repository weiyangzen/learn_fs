# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_devfreq.c

## Purpose
Implements devfreq integration for MSM GPUs. It samples GPU busy cycles, drives OPP/frequency changes through devfreq, handles active/idle frequency transitions, provides temporary PM QoS boost, supports thermal cooling registration, and coordinates with GPU runtime suspend/resume.

## Important APIs, Types, and Functions
- `msm_devfreq_init()` initializes governor tuning, PM QoS boost request, devfreq device, cooling device, and hrtimer-backed idle/boost work.
- `msm_devfreq_cleanup()` unregisters cooling and removes QoS request.
- `msm_devfreq_resume()` and `msm_devfreq_suspend()` update suspended state, baseline busy counter/time, devfreq device state, and cancel delayed work.
- `msm_devfreq_active()` restores the shadow idle frequency and boosts after long idle periods.
- `msm_devfreq_idle()` queues a delayed clamp-to-idle operation.
- `msm_devfreq_boost()` raises the PM QoS minimum frequency for one polling interval.
- `msm_devfreq_target()`, `msm_devfreq_get_dev_status()`, and `msm_devfreq_get_cur_freq()` implement `devfreq_dev_profile`.

## Control Flow
At init, devfreq is enabled only when the GPU supplies `gpu_busy`. The simple_ondemand governor is tuned to ramp up at 50% utilization. While active, target frequency changes call a generation hook `gpu_set_freq()` or `dev_pm_opp_set_rate()`. When the GPU becomes idle, a short hrtimer queues work that records the current frequency as `idle_freq` and optionally clamps hardware to a minimum/zero target. When active again, the saved frequency is restored under the devfreq lock and a boost may be applied if the idle interval would otherwise hide real demand from the governor.

## State and Persistence
State lives in `gpu->devfreq`: devfreq handle, mutex, idle shadow frequency, boost QoS request, busy-cycle baseline, sampling time, idle time, hrtimer works, and suspended flag. Thermal cooling state is stored in `gpu->cooling`. No persistent disk state.

## Dependencies and Integration Points
Depends on Linux devfreq, OPP, PM QoS, devfreq cooling, hrtimer/kthread helpers from `msm_io_utils.c`, tracepoints, and generation-specific busy/frequency hooks from `msm_gpu_funcs`. GPU core calls active/idle/resume/suspend at submit/retire and PM boundaries.

## Risks
Risks include unit mismatch between devfreq Hz and PM QoS kHz, governor confusion during idle clamps, racing target callbacks with suspend or idle work, and stale busy-cycle baselines. The code uses `df->lock` and `df->devfreq->lock`, cancels hrtimer work on suspend, and keeps an idle shadow frequency to preserve governor state.

## Test Signals
Observe `trace_msm_gpu_freq_change`, devfreq sysfs current frequency, thermal cooling registration, correct active/idle transitions during bursty workloads, no QoS leak after boost expiry, stable runtime suspend/resume, and sane busy_time/total_time samples.
