# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-kprobe.sh

## Purpose

`test-kprobe.sh` validates livepatch interaction with kprobes on the same target function. It distinguishes kprobes with a post handler, which use IPMODIFY and conflict with livepatch ftrace registration, from kprobes without a post handler.

## Important APIs, Types, and Functions

The script checks `/proc/kallsyms` for `kprobe_ftrace_ops`, toggles `/sys/kernel/debug/kprobes/enabled`, loads `test_klp_kprobe` with `has_post_handler=true/false`, and loads or fails `test_klp_livepatch`.

## Control Flow and State

It first skips if the kernel lacks kprobes-on-ftrace support. With post handler enabled, livepatch load must fail with handler-registration errors. Without the post handler, the livepatch should load, then the kprobe and livepatch are removed in order.

## Dependencies and Integration Points

It depends on kprobe-on-ftrace support, kprobes debugfs, the kprobe test module, the livepatch test module, and exact dmesg matching.

## Risks and Test Signals

Risks are allowing multiple IPMODIFY users on the same function or over-rejecting non-conflicting kprobes. Signals are load failure with `Device or resource busy` in the post-handler case and successful patch/unpatch in the no-post-handler case.
