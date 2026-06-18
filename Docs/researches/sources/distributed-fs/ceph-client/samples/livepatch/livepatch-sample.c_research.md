# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-sample.c

Purpose: minimal kernel livepatch that replaces `/proc/cmdline` display function.

Important APIs/functions: replacement `livepatch_cmdline_proc_show`, `struct klp_func` targeting `cmdline_proc_show`, vmlinux `struct klp_object`, `struct klp_patch`, `klp_enable_patch`, and `MODULE_INFO(livepatch, "Y")`.

Control flow: init enables the patch; after transition, reads of `/proc/cmdline` call the replacement and print a fixed string. Exit is empty; the patch must be disabled via livepatch sysfs before removal.

State and persistence: livepatch core state and sysfs `enabled` flag while module exists.

Dependencies and integration: depends on target symbol name and livepatch infrastructure.

Risks: symbol name changes break the sample. Empty exit requires users to disable through `/sys/kernel/livepatch/.../enabled`.

Test signals: compare `/proc/cmdline` before/after load, disable through sysfs, confirm original output returns, then remove module.
