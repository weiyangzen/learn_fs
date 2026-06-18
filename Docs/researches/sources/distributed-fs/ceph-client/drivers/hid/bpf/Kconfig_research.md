# sources/distributed-fs/ceph-client/drivers/hid/bpf/Kconfig

## Purpose

This Kconfig file exposes HID-BPF support, allowing eBPF programs to fix HID report descriptors, rewrite HID events, and issue selected HID operations through BPF kfuncs and struct_ops.

## Important APIs, Types, and Functions

The sole symbol is `HID_BPF`, a boolean "HID-BPF support". It depends on `BPF`, `BPF_SYSCALL`, `DYNAMIC_FTRACE_WITH_DIRECT_CALLS`, and `BPF_JIT`, and defaults to enabled when dependencies are present.

## Control Flow

When selected from the parent HID Kconfig, Kbuild enters `drivers/hid/bpf/` and builds the HID-BPF dispatcher and struct_ops support. If dependencies are unavailable, HID core builds without this extension.

## State and Persistence Behavior

This file persists a build-time feature choice. Runtime per-device BPF state is initialized by HID core only when the built code is present.

## Dependencies and Integration Points

The dependency set ties HID-BPF to the BPF verifier/runtime, syscall loading path, JIT support, and tracing direct-call infrastructure needed for struct_ops and kfunc calls.

## Risks and Test Signals

Dependency mistakes can produce build failures or a selectable feature that cannot load programs. Test signals include `CONFIG_HID_BPF=y` builds, BPF selftests using HID struct_ops, and module load paths on kernels with and without BPF JIT.
