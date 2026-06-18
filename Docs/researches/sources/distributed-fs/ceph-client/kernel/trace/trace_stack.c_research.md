# sources/distributed-fs/ceph-client/kernel/trace/trace_stack.c

## Purpose

`trace_stack.c` implements the kernel stack tracer. It uses ftrace callbacks to measure current stack depth, records the largest observed stack with symbols and per-frame sizes, exposes tracefs files, supports dynamic ftrace filtering, and registers a sysctl to enable or disable tracing. The complete 600-line file was read.

## Important APIs, Types, and Functions

Important functions include `check_stack()`, `stack_trace_call()`, `stack_max_size_read()`, `stack_max_size_write()`, `stack_trace_sysctl()`, boot parser `enable_stacktrace()`, `stack_trace_init()`, and `init_trace_stack_sysctls()`. Global state includes stack trace arrays, max size, lock, per-CPU recursion guard, sysctl mutex, and enable flag.

## Control Flow

When enabled, ftrace calls `stack_trace_call()`, which disables preemption, increments a recursion guard, verifies RCU watching, adjusts IP, and calls `check_stack()`. `check_stack()` computes stack usage, ignores non-task stacks and NMI, records a new max under lock, saves stack entries, maps return addresses to stack offsets, handles architecture shift rules, and BUGs on stack-end corruption. Seq reads print the stored max stack.

## State and Persistence Behavior

The maximum stack record persists globally until overwritten or reset through `stack_max_size`. `stack_tracer_enabled` persists through sysctl and boot setup. Optional filter text from `stacktrace_filter=` is initdata applied during init.

## Dependencies and Integration Points

It depends on ftrace, stacktrace APIs, task stack helpers, tracefs, security lockdown, sysctl, kallsyms formatting, command-line setup, and dynamic ftrace filters.

## Risks and Edge Cases

Stack tracing runs from ftrace and must avoid recursion, NMI deadlocks, non-task stacks, and RCU-off contexts. Frame calibration is architecture-sensitive. Stack walking can miss return addresses. Incorrect enable/filter ordering can leave callbacks active unexpectedly.

## Test Signals

Boot with `stacktrace`, toggle `/proc/sys/kernel/stack_tracer_enabled`, read `stack_trace`, reset `stack_max_size`, apply `stack_trace_filter`, and validate deep call-chain output.
