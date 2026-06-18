# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_atomic_replace.c

## Purpose

`test_klp_atomic_replace.c` is a livepatch test module that patches `meminfo_proc_show` and optionally sets `.replace` to exercise atomic-replace semantics.

## Important APIs, Types, and Functions

It defines module parameter `replace`, replacement `livepatch_meminfo_proc_show()`, `struct klp_func`, `struct klp_object`, `struct klp_patch`, and init/exit functions using `klp_enable_patch()`.

## Control Flow and State

On module load, `test_klp_atomic_replace_init()` copies the parameter into `patch.replace` and enables the patch. The patched proc show function prints a module-specific live-patched string. Module exit has no cleanup logic beyond livepatch core handling.

## Dependencies and Integration Points

It depends on livepatch core, procfs `meminfo_proc_show`, and the livepatch scripts that read `/proc/meminfo` and inspect replace behavior.

## Risks and Test Signals

Risks include target symbol name drift and incorrect replace-flag propagation. Signals are `/proc/meminfo` returning the live-patched string and sysfs `replace` reporting the requested value.
