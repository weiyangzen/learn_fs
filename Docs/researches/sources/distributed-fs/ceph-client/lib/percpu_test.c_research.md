# sources/distributed-fs/ceph-client/lib/percpu_test.c

## Purpose
Provides a load-time module test for low-level `this_cpu` and `__this_cpu` arithmetic semantics, especially signed/unsigned subtraction and widening behavior.

## APIs, Control Flow, and State
Defines per-CPU `long_counter` and `ulong_counter`, a `CHECK()` macro comparing native and per-CPU values to expected results, and `percpu_test_init()`. Init disables preemption, performs a sequence of adds, subtracts, decrements, and return-value operations with signed, unsigned, and volatile operands, emits warnings on mismatch, reenables preemption, logs completion, and returns `-EAGAIN` so the module unloads immediately. Exit is empty.

## Dependencies, Integration, Risks, and Tests
Depends on module support, per-CPU accessors, and kernel warning infrastructure. Risks are limited to test maintenance: expectations are architecture/compiler-sensitive and the module intentionally fails load with `-EAGAIN`. Test signals are absence of `WARN()` output during load, coverage across compilers/architectures, and correct behavior around unsigned wrap to `ULONG_MAX`.
