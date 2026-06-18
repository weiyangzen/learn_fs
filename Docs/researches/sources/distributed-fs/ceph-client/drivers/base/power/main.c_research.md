# sources/distributed-fs/ceph-client/drivers/base/power/main.c

## Purpose
Implements the system-wide device PM core: device registration into PM lists, prepare/suspend/late/noirq and resume/noirq/early/complete sequencing, dependency-aware asynchronous PM, direct-complete and smart-suspend optimization, wakeup propagation, PM watchdog support, and exported PM iteration/wait helpers.

## Important APIs, Types, And Functions
Exports `pm_hibernate_is_recovering()`, `dpm_resume_start()`, `dpm_resume_end()`, `dpm_suspend_end()`, `dpm_suspend_start()`, `__suspend_report_result()`, `device_pm_wait_for_dev()`, and `dpm_for_each_dev()`. Device lifecycle helpers include `device_pm_sleep_init()`, `device_pm_add()`, `device_pm_remove()`, move helpers, `device_pm_check_callbacks()`, `dev_pm_skip_suspend()`, and `dev_pm_skip_resume()`. Core lists are `dpm_list`, `dpm_prepared_list`, `dpm_suspended_list`, `dpm_late_early_list`, and `dpm_noirq_list`.

## Control Flow
Registered devices enter `dpm_list` in discovery order. Suspend starts with `dpm_prepare()`, which waits for probes, blocks probing, suspends thermal control, calls `prepare()`, blocks runtime PM, and moves devices to `dpm_prepared_list`. `dpm_suspend()`, `dpm_suspend_late()`, and `dpm_suspend_noirq()` walk from leaf devices toward parents/suppliers, using completions to respect child and device-link dependencies and moving devices through staged lists. Resume reverses the direction from roots toward children/consumers through noirq, early, normal, and complete phases. Callback selection prioritizes PM domain, type, class, bus, then driver callbacks, with legacy bus callbacks as fallback. Errors set `async_error`, save failed step/device, complete pending devices, and trigger partial resume.

## State And Persistence
State lives in `dev->power`: list entry, completion, `is_prepared`, `is_suspended`, `is_late_suspended`, `is_noirq_suspended`, `direct_complete`, `smart_suspend`, `must_resume`, wakeup flags, async flags, and callback-presence cache. Global state includes `pm_transition`, `async_error`, and PM lists protected by `dpm_list_mtx`. Nothing is persisted across boot.

## Dependencies And Integration
Integrates with the driver core, runtime PM, wake IRQs, device links, async framework, suspend tracing, cpufreq/devfreq/thermal PM hooks, PM trace, PM domains, syscore flags, wakeup sources, and optional DPM watchdog timers.

## Risks And Test Signals
Risks are high: dependency ordering regressions, races with device removal during async PM, incorrect direct-complete handling, runtime PM disable/enable imbalance, wakeup propagation loss, missed completion causing suspend hangs, and wrong rollback after phase errors. Test signals include suspend/hibernate/resume stress tests, async suspend enabled/disabled runs, device-link dependency tests, wakeup abort tests, DPM watchdog coverage, runtime PM interaction tests, and tracing of failed PM steps.
