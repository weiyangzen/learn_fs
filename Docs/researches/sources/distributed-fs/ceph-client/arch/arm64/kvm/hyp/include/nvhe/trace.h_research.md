# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/trace.h

## Purpose

This header defines the nVHE EL2 tracing interface, including remote event formatting, event emission helpers, and host-call entry points for trace control.

## Important APIs, Types, And Functions

It provides `__tracing_get_vcpu_pid()`, the `HYP_EVENT()` expansion for trace emitters, `tracing_reserve_entry()`, `tracing_commit_entry()`, and control APIs `__tracing_load()`, `__tracing_unload()`, `__tracing_enable()`, `__tracing_swap_reader()`, `__tracing_update_clock()`, `__tracing_reset()`, and `__tracing_enable_event()`.

## Control Flow

When tracing is enabled, each generated `trace_<event>()` checks the event atomic, reserves a remote entry, writes the event ID and assignment payload, and commits. Without tracing, emitters are inline no-ops and control APIs return `-ENODEV` or do nothing.

## State And Persistence Behavior

Enabled builds persist descriptor mappings, event IDs, per-event enabled atomics, ring-buffer state, and clock data. The helper derives PID from the running vCPU in host context.

## Dependencies And Integration Points

It integrates with `linux/trace_remote_event.h`, `asm/kvm_hyptrace.h`, `asm/kvm_hypevents.h`, and nVHE host hypcalls in `hyp-main.c`.

## Risks And Test Signals

Risks are tracing from unsafe contexts, failed reservations, stale vCPU PID, and host-controlled descriptor trust boundaries. Test signals are enable/disable event filtering, buffer swap/reset, clock updates, and trace output for hyp enter/exit events.
