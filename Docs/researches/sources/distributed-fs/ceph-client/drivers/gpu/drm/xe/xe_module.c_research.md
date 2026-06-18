
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.c

## Purpose

`xe_module.c` is the Linux module entry point for the Xe driver. It defines module parameters, runs module-wide initialization functions in order, unwinds on failure, and performs reverse-order cleanup on module unload.

## Important APIs, Types, and Functions

- Global `struct xe_modparam xe_modparam` with defaults for display probing, GuC log level, firmware paths, force-probe, VRAM BAR size, wedged policy, SVM notifier size, and SR-IOV max VFs.
- Module parameters declared with `module_param_named*` and `MODULE_PARM_DESC`.
- `xe_check_nomodeset()` rejects loading when firmware-only drivers are requested.
- `struct init_funcs` plus `init_funcs[]` sequences configfs, hw fence, sched job, PCI driver, observation sysctl, and PM init.
- `xe_init()` and `xe_exit()` are registered with `module_init`/`module_exit`.

## Control Flow

Module load iterates `init_funcs[]` in order. On the first error it logs the failing init function pointer and unwinds only functions whose init already ran. Module unload iterates the table in reverse and calls any exit function. Some entries, like `xe_pm_module_init`, have no exit callback.

## State and Persistence Behavior

`xe_modparam` stores process-wide module configuration. Init functions register global subsystems such as PCI driver binding, sysctl entries, configfs, and scheduler/fence infrastructure. Unload removes only entries with explicit exits.

## Dependencies and Integration Points

This file ties together DRM module support, Xe PCI probing, PM, scheduler jobs, hw fences, configfs, and observation sysctl registration. It includes module metadata for author, description, and license.

## Risks and Edge Cases

- Init ordering is important; PCI registration occurs after shared infrastructure and before observation sysctl/PM in this table.
- Unsafe module parameters can alter firmware paths and force-probe behavior early in driver load.
- Failure unwind only calls exits for prior entries, so entries with side effects but no exit must be safe on later failure or be intentionally one-way.

## Test Signals

Module load/unload testing, parameter parsing tests, forced init failure injection, `nomodeset`/firmware-only behavior, and repeated bind/unbind cycles are useful signals.
