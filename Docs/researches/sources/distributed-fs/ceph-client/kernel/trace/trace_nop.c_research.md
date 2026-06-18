# sources/distributed-fs/ceph-client/kernel/trace/trace_nop.c

## Purpose
Defines the `nop` tracer, the baseline tracer that performs no tracing work but provides a valid current-tracer target and a small tracer-option callback example.

## APIs, Control Flow, and State
The global `nop_trace` `struct tracer` names the tracer `nop`, provides init/reset callbacks, optional selftest hook, tracer flags, set-flag callback, and allows tracing instances. `nop_trace_init()` stores the active `trace_array` in `ctx_trace` and calls an empty start function; reset calls an empty stop function. Two options are declared: `test_nop_accept`, which `nop_set_flag()` accepts, and `test_nop_refuse`, which it rejects with `-EINVAL`. The tracing framework updates `nop_flags.val` only when the callback succeeds.

## Dependencies, Integration, Risks, and Tests
This file depends on core ftrace tracer registration structures from `trace.h`. It is usually registered by common tracing initialization rather than an initcall in this file. Integration points are `current_tracer`, trace instances, trace option display, and ftrace startup selftests.

Risks are intentionally low, but the file is useful as a sentinel: if the `nop` tracer cannot initialize or reset cleanly, the tracing subsystem's baseline state is broken. Test signals include switching to `nop`, toggling `test_nop_accept` and observing it persist, toggling `test_nop_refuse` and observing `-EINVAL`, instance support, and `trace_selftest_startup_nop` when enabled.
