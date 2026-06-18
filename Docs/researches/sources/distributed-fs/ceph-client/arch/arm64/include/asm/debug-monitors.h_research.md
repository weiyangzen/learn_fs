## sources/distributed-fs/ceph-client/arch/arm64/include/asm/debug-monitors.h

Purpose: declares arm64 debug monitor state, breakpoint/single-step controls, and debug exception hooks.

Important APIs/types/functions: provides MDSCR/KDE/MDE/SS constants, `DBG_ACTIVE_EL0/EL1`, hooks for enabling/disabling debug monitors, single-step state helpers, breakpoint handlers, and user/kernel debug control interfaces.

Control flow: implementation code toggles MDSCR bits and routes debug exceptions through registered hooks.

State and persistence: per-CPU debug register state and per-thread single-step flags live outside the header; this file defines the contract.

Dependencies and integration: used by ptrace, hardware breakpoints, kprobes, kgdb, perf, and exception handlers.

Risks: incorrect debug mask handling can expose kernel debugging to user mode or break single-step. Test signals are ptrace single-step tests, hw breakpoint tests, kprobe/kgdb tests, and perf watchpoints.
