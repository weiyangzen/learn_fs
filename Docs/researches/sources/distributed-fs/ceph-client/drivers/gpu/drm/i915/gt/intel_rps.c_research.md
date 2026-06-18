# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rps.c

## Purpose
`intel_rps.c` implements i915 Render Power States frequency control. It initializes hardware frequency caps, enables dynamic reclocking, handles PM interrupts or timer-based busy sampling, processes wait boosting, exposes frequency setters/getters, integrates GuC SLPC delegation, and provides Gen5 IPS callbacks.

## Important APIs, Types, And Functions
Public APIs include `intel_rps_init_early()`, `intel_rps_init()`, `intel_rps_enable()`, `intel_rps_disable()`, `intel_rps_park()`, `intel_rps_unpark()`, `intel_rps_boost()`, frequency getters/setters, threshold setters, IRQ handlers, `gen6_rps_frequency_dump()`, IPS exports such as `i915_read_mch_val()`, and the display-facing `i915_display_rps_interface`. Key internal functions are `rps_timer()`, `rps_work()`, `rps_set()`, Gen5/6/8/9/VLV/CHV enable/init helpers, cap readers, conversion helpers, and interrupt mask helpers.

## Control Flow
Early init creates locks, timer, work item, and wait counters. Init reads platform caps and derives hard limits, soft limits, boost, idle, efficient frequency, thresholds, and interrupt mask must-be-zero bits. Enable chooses a platform path, programs thresholds/control registers, resets to minimum, and selects either busy-stat timer or PM interrupts. Unpark activates RPS and starts monitoring; park stops monitoring, drops frequency to idle with forcewake if needed, and biases the next resume downward. IRQs mask RPS events and queue `rps_work()`, which combines PM events, VLV C0 workaround data, and client boost waiters to choose a new clamped frequency.

## State, Persistence, And Dependencies
Persistent state is `struct intel_rps`: locks, flags, timer/work, PM event masks, current/last/soft/hard frequencies, thresholds, boost counters, EI samples, and Gen5 IPS accounting. Hardware state lives in RP control/status registers, Punit/IOSF registers, interrupt masks, and SLPC state when GuC owns control. Dependencies include runtime PM, uncore forcewake, GT PM IRQ helpers, pcode, VLV sideband, display RPS hooks, engine busy stats, workqueues, and `intel_ips`.

## Integration Points
GT power management calls enable/disable/park/unpark. Request wait paths call `intel_rps_boost()` and retirement decrements waiters. Sysfs/debugfs-style controls call min/max/boost/threshold accessors. Display code calls the exported display RPS interface. GuC SLPC paths bypass local control for many operations.

## Risks
Locking spans `rps->lock`, `rps->power.mutex`, `gt->irq_lock`, and `mchdev_lock`; ordering mistakes can deadlock or race with interrupts. Frequency units differ by platform and SLPC, so conversion bugs can silently set wrong limits. PM interrupt masks include platform bits that must remain unmasked. VLV/CHV IOSF and Gen5 IPS paths are hardware-specific. Timer busy heuristics can oscillate or underboost multi-engine workloads.

## Test Signals
Selftests include `selftest_rps.c` and `selftest_slpc.c`. Runtime tests should exercise min/max/boost sysfs controls, waitboost under blocked requests, park/unpark loops, suspend/resume sanitize, PM interrupt storms, timer-based busy stats, GuC SLPC mode, VLV/CHV sideband reads, and Gen5 IPS exported callbacks.
