<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/preempt.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/preempt.h

## Purpose

`linux/preempt.h` provides minimal preemption accounting for userspace tests.

## Important APIs, Types, and Functions

It declares `extern int preempt_count`, maps `preempt_disable()` and `preempt_enable()` to atomic increment/decrement of that count, and defines `in_interrupt()` to return false.

## Control Flow and State

Only `preempt_count` changes. There is no scheduler or interrupt context emulation.

## Dependencies and Integration Points

It depends on Userspace RCU atomics and `linux.c` defining `preempt_count`. Imported kernel code can assert or inspect preemption-like state.

## Risks and Test Signals

Risks include masking bugs that depend on real preemption or interrupt context. Counter balance can still be observed by tests; successful shared-test execution validates the stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/preempt.h -->
