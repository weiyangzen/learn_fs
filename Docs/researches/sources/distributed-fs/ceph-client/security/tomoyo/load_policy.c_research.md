# sources/distributed-fs/ceph-client/security/tomoyo/load_policy.c

## Purpose

`load_policy.c` optionally invokes the TOMOYO userspace policy loader during early boot. When userspace loading is enabled, it waits until a configured activation trigger program is executed, runs the configured loader, and validates loaded profiles before MAC activation.

## Important APIs, types, and functions

`tomoyo_load_policy()` is the exported entry point. Boot parameters are parsed by `tomoyo_loader_setup()` for `TOMOYO_loader=` and `tomoyo_trigger_setup()` for `TOMOYO_trigger=`. `tomoyo_policy_loader_exists()` verifies the loader path with `kern_path()`. All code is compiled out when `CONFIG_SECURITY_TOMOYO_OMIT_USERSPACE_LOADER` is set.

## Control flow

`tomoyo_load_policy()` returns immediately if policy is already loaded, if it has already attempted loading, if the current executable is not the activation trigger, or if the loader path does not exist. On the first matching trigger it marks `done`, logs the loader call, builds a minimal argv/envp, invokes `call_usermodehelper(..., UMH_WAIT_PROC)`, then calls `tomoyo_check_profile()` to validate and activate policy.

## State and persistence behavior

The file stores static loader and trigger path pointers populated from boot parameters or Kconfig defaults. A static `done` flag prevents repeated loader invocation. It mutates global policy activation indirectly through `tomoyo_check_profile()`, which sets `tomoyo_policy_loaded` after validating profiles.

## Dependencies and integration points

The file depends on Kconfig symbols `CONFIG_SECURITY_TOMOYO_POLICY_LOADER` and `CONFIG_SECURITY_TOMOYO_ACTIVATION_TRIGGER`, kernel path lookup, `call_usermodehelper`, and `tomoyo_check_profile()`. It is invoked from exec-domain flow when an executable name is available for trigger comparison.

## Risks

If the trigger path does not match the resolved executable name used by callers, policy loading never runs. If the loader is absent, TOMOYO logs and does not activate MAC through this path. The `done` flag is set before the helper result is checked, so a failed helper invocation is not retried. Boot environments without `/sbin`-style paths or with custom init systems need correct kernel parameters.

## Test signals

Tests should cover default and boot-parameter loader/trigger paths, missing loader behavior, single invocation despite multiple trigger execs, helper failure handling, `CONFIG_SECURITY_TOMOYO_OMIT_USERSPACE_LOADER` builds, and successful loader-to-profile-validation activation.
