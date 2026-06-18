# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/functions.sh

## Purpose

`functions.sh` is the livepatch selftest harness library. It handles prerequisite checks, sysfs/debugfs/tracing state save and restore, module load/unload, livepatch transition waiting, dmesg canarying, exact log comparison, sysfs assertions, and ftrace setup.

## Important APIs, Types, and Functions

Key functions are `setup_config()`, `push_config()`, `pop_config()`, `set_dynamic_debug()`, `set_ftrace_enabled()`, `load_mod()`, `load_lp_nowait()`, `load_lp()`, `load_failing_mod()`, `unload_mod()`, `disable_lp()`, `set_pre_patch_ret()`, `start_test()`, `check_result()`, `check_sysfs_rights()`, `check_sysfs_value()`, `trace_function()`, and `check_traced_functions()`.

## Control Flow and State

Each script sources this file, calls `setup_config()`, and then sequences module operations. The harness writes markers to `/dev/kmsg`, waits for `/sys/module` and `/sys/kernel/livepatch` state, polls livepatch `transition`, snapshots current debug/tracing/sysctl state, and restores it on exit through a trap. `check_result()` treats filtered dmesg text as an exact test oracle.

## Dependencies and Integration Points

It depends on root, `KDIR`, livepatch sysfs, debugfs/tracing paths, kprobes control, dynamic debug, `insmod`, `rmmod`, `modinfo`, `dmesg`, `sysctl`, and standard shell tools.

## Risks and Test Signals

Risks include unbounded waits, dmesg buffer overrun, path differences between tracefs/debugfs, not restoring global kernel state, and brittle exact-output comparisons. Signals are clean skips for missing root/KDIR, completed transition polling, exact `check_result()` matches, and restored sysfs/tracing state on exit.
