# sources/distributed-fs/ceph-client/arch/x86/kernel/trace.c

## Purpose
`trace.c` provides x86 OS noise tracer integration for local APIC and IPI vectors, registering IRQ tracepoints so osnoise can attribute interrupt entry/exit time.

## Important APIs, Types, And Functions
Public hooks are `osnoise_arch_register()` and `osnoise_arch_unregister()`. Internal callbacks `trace_intel_irq_entry()` and `trace_intel_irq_exit()` call `osnoise_trace_irq_entry()` and `osnoise_trace_irq_exit()`.

## Control Flow
Registration installs callbacks for local timer, optional thermal/deferred-error/threshold vectors, SMP call-function and reschedule IPIs, optional IRQ work, platform IPI, error APIC, and spurious APIC. Any failure unwinds prior registrations in reverse order and returns `-EINVAL`. Unregister removes all configured callbacks.

## State, Persistence, Dependencies, Integration
Persistent state is the tracepoint registration set. Dependencies include `CONFIG_OSNOISE_TRACER`, `CONFIG_X86_LOCAL_APIC`, generated x86 IRQ vector tracepoints, and optional APIC/MCE/SMP/IRQ_WORK config symbols. The generic osnoise tracer calls these arch hooks.

## Risks And Test Signals
Register/unregister pairing must stay exact across config guards. Exit labels are user-visible tracer names. Test osnoise with different vector configs, registration failure injection, unregister after full registration, and reports for timer/IPI/APIC vectors.
