# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_PAGEFAULT`, an RT-application monitor that reports page faults from real-time tasks.

## Important APIs, Types, and Functions

It depends on `RV`, `RV_MON_RTAPP`, `X86 || RISCV`, and `MMU`; selects `RV_LTL_MONITOR` and `LTL_MON_EVENTS_ID`; and defaults to enabled.

## Control Flow

Selecting the symbol builds an LTL monitor under the `rtapp` container and enables ID-aware LTL trace events.

## State and Persistence Behavior

Only compile-time configuration is held here.

## Dependencies and Integration Points

The architecture dependency reflects page-fault tracepoint availability. The help text frames this as safe for production when disabled at runtime.

## Risks and Edge Cases

Unsupported architectures cannot build it even if similar page-fault hooks exist under different names.

## Test Signals

Kconfig tests should cover x86/RISC-V MMU builds and ensure no symbol on unsupported/no-MMU configurations.
