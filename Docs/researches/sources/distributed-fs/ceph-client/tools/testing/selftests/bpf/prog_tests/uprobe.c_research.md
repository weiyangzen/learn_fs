# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uprobe.c

## Purpose
Tests basic uprobe and uretprobe attachment to selftest binaries/libraries, symbol-version resolution, same-offset autoattach, and x86 register/IP modification by uprobe BPF programs.

## APIs, Types, and Functions
Entry point `test_uprobe()` runs `test_uprobe_attach()` and x86-only `test_uprobe_regs_change()`. Helpers spawn `./urandom_read`, attach to symbols in `liburandom_read.so`, and define naked assembly triggers for register snapshots and IP redirection.

## Control Flow, State, and Persistence
`test_uprobe_attach()` loads `test_uprobe`, starts `urandom_read`, sets target pid, confirms unversioned ambiguous `urandlib_api` attach fails, attaches a versioned symbol manually, autoattaches the remaining probes, triggers the child by closing the pipe, and checks BSS results. x86 register tests attach to `/proc/self/exe`, run assembly that captures registers before and after probe execution, and assert either register replacement or redirected return target.

## Dependencies and Integration
Depends on `test_uprobe.skel.h`, selftest helper binaries `urandom_read` and `liburandom_read.so`, libbpf uprobe attach APIs, `/proc/self/exe`, and x86 register layout for the assembly subtests.

## Risks and Test Signals
Risks include symbol versioning differences, helper binary availability, architecture-specific assembly, and compiler instrumentation affecting naked functions. Signals are expected attach conflict for ambiguous symbol, correct result counters for versioned/same-offset probes, and expected register/IP changes on x86.
