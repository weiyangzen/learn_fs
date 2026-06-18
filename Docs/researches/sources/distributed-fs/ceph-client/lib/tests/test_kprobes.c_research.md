<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_kprobes.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_kprobes.c

## Purpose
KUnit sanity tests for kprobe and kretprobe registration, handler invocation, missed-recursion accounting, multi-probe registration, and optional stacktrace correctness on kretprobe trampolines.

## APIs, Types, and Functions
Uses `struct kprobe`, `struct kretprobe`, `register_kprobe()`, `register_kprobes()`, `unregister_kprobe()`, `register_kretprobe()`, `register_kretprobes()`, `regs_return_value()`, `stack_trace_save()`, and `stack_trace_save_regs()`. Target functions include `kprobe_target()`, `kprobe_target2()`, `kprobe_recursed_target()`, and stacktrace driver/target functions. `KP_CLEAR()` resets probe fields before reuse.

## Control Flow, State, and Persistence
`kprobes_test_init()` clears static probe structures, assigns function pointers to avoid inlining, and seeds `rand1`. Tests register probes by symbol name, call target functions, assert pre/post or return handler side effects, and unregister. The recursion test places a kprobe on `kprobe_recursed_target()` while handlers call that target and expects `nmissed == 2`. Kretprobe tests run only under `CONFIG_KRETPROBES`; stacktrace tests additionally require `CONFIG_ARCH_CORRECT_STACKTRACE_ON_KRETPROBE` and verify saved stack frames contain original return addresses.

## Dependencies and Integration
Depends on kprobes/kretprobes, random generation, KUnit, stacktrace support, architecture unwind behavior, and relevant config options. It integrates with the `kprobes_test` suite and exercises low-level dynamic instrumentation.

## Risks and Test Signals
Risks include architecture-specific unwinder behavior, module-vs-built-in differences for `stack_trace_save_regs()`, global static probe state, target inlining, and unregister cleanup after partial failures. Test signals include handler values, return-value checks, recursion miss count, batch register/unregister behavior, and nested kretprobe stacktrace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_kprobes.c -->
