# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.c

## Purpose
This file owns Panfrost device bring-up, teardown, power-management callbacks, GPU reset orchestration, reset/clock/regulator/power-domain setup, and exception-name lookup.

## Important APIs, Types, and Functions
Public functions are `panfrost_device_init`, `panfrost_device_fini`, `panfrost_device_reset`, `panfrost_exception_name`, and `panfrost_exception_needs_reset`. Internal setup covers reset controls, clocks, regulators, multi-power-domain links, runtime/system PM, and the exception table.

## Control Flow
Initialization creates locks/lists, attaches power domains, deasserts resets, enables clocks, initializes devfreq, optionally enables regulators if OPP did not take ownership, maps MMIO, initializes GPU, MMU, job manager, performance counters, and GEM. Failures unwind in reverse. Runtime resume optionally deasserts reset/enables clocks, resets the GPU stack, and resumes devfreq. Runtime suspend refuses non-idle job manager state, suspends devfreq and IRQs, powers off GPU blocks, and optionally disables clocks/asserts reset. System suspend/resume additionally handles platform PM feature bits and OPP regulator state.

## State and Persistence Behavior
The file mutates the device's locks, lists, reset/clock/regulator/domain handles, `iomem`, power-feature-dependent hardware state, IRQ suspension bits, address-space state through reset, and devfreq state.

## Dependencies and Integration Points
It coordinates all major Panfrost subsystems: GPU, MMU, job manager, GEM, devfreq, performance counters, reset controls, clocks, regulators, PM domains, runtime PM, and OPP.

## Risks
Initialization unwind order must mirror setup or clocks/regulators/IRQs can leak. Runtime suspend must only proceed when the job manager is idle. PM feature bits vary by compatible data, so wrong OF match data can disable rails or clocks incorrectly. Reset reinitializes GPU/MMU/JM state and must be synchronized with scheduler recovery.

## Test Signals
Signals include probe failure injection at each init stage, runtime autosuspend under idle and active jobs, system suspend/resume on all compatible PM feature combinations, reset after GPU faults, and exception-name coverage for fault logs.
