# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_callbacks_demo2.c

## Purpose

`test_klp_callbacks_demo2.c` is a second callback livepatch module used to test multiple livepatches and atomic replace without external module targets.

## Important APIs, Types, and Functions

It defines parameter `replace`, callback logging functions, a no-function vmlinux `klp_object`, `struct klp_patch`, and init logic that sets `patch.replace` before `klp_enable_patch()`.

## Control Flow and State

On load it applies a vmlinux-only livepatch whose callbacks log patch and unpatch phases. On unload it relies on livepatch core state; there is no custom exit cleanup.

## Dependencies and Integration Points

It integrates with `test-callbacks.sh` scenarios for multiple livepatches and replace behavior.

## Risks and Test Signals

Risks are replace parameter not reflected in the patch or callbacks firing when atomic replacement should skip older patch unpatch callbacks. Signals are exact callback logs and sysfs replace/stack behavior.
