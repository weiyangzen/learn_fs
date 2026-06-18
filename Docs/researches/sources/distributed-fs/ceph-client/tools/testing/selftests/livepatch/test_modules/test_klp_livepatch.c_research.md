# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_livepatch.c

## Purpose

`test_klp_livepatch.c` is the basic vmlinux livepatch module. It replaces `cmdline_proc_show` so `/proc/cmdline` reports a live-patched string.

## Important APIs, Types, and Functions

It defines replacement `livepatch_cmdline_proc_show()`, a `klp_func` mapping old name `cmdline_proc_show` to the replacement, a vmlinux `klp_object`, `struct klp_patch`, and init/exit functions.

## Control Flow and State

On load, `klp_enable_patch()` activates the replacement. Reads of `/proc/cmdline` flow through the replacement until the patch is disabled and unloaded. The module itself stores only static patch descriptors.

## Dependencies and Integration Points

It is used by most livepatch scripts, depends on the `cmdline_proc_show` symbol and livepatch core, and integrates with ftrace/kprobe/sysfs tests.

## Risks and Test Signals

Risks are symbol rename, livepatch registration failure, or stale replacement after disable. Signals are `/proc/cmdline` showing and then no longer showing `test_klp_livepatch: this has been live patched`.
