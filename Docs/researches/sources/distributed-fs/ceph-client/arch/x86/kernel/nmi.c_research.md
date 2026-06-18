# sources/distributed-fs/ceph-client/arch/x86/kernel/nmi.c

## Purpose
Implements x86 non-maskable interrupt dispatch, accounting, nested-NMI containment, crash shootdown integration, and diagnostic stall reporting. It multiplexes architectural NMI entry events into registered Linux NMI handler chains for local, unknown, PCI SERR, and I/O-check NMIs.

## APIs, Types, And Functions
Key state is `struct nmi_desc`, the `nmi_desc[NMI_MAX]` handler registry, per-CPU `struct nmi_stats`, `ignore_nmis`, `unknown_nmi_panic`, `panic_on_unrecovered_nmi`, `panic_on_io_nmi`, per-CPU nested state `nmi_state`, `nmi_cr2`, and `nmi_dr7`. Public integration points include `__register_nmi_handler()`, `unregister_nmi_handler()`, `set_emergency_nmi_handler()`, `exc_nmi`, KVM's `exc_nmi_kvm_vmx` wrapper, `nmi_backtrace_stall_snap()`, `nmi_backtrace_stall_check()`, `stop_nmi()`, `restart_nmi()`, and `local_touch_nmi()`.

## Control Flow
NMI entry reaches `exc_nmi`, which handles SEV-ES completion, ignores offline CPUs except microcode NMIs, latches nested NMIs via the per-CPU `NMI_NOT_RUNNING/NMI_EXECUTING/NMI_LATCHED` state machine, saves CR2 and debug state, enters irqentry NMI context, and invokes `default_do_nmi()` unless NMIs are globally ignored. `default_do_nmi()` first services microcode NMIs, then local NMI handlers, then external reason-port sources under `nmi_reason_lock`, then unknown NMI handlers. Back-to-back NMI detection uses per-CPU RIP tracking and `swallow_nmi` to suppress some already-handled edge-triggered events. FRED builds use a simpler NMI entry because FRED preserves CR2/DR6 semantics in the event frame.

## State And Persistence
Handler lists are RCU-protected and spinlock-updated; unregister synchronizes before reinitializing list nodes. The emergency handler is a direct pointer intended for crash contexts and is published with a write barrier. Per-CPU counters persist for runtime diagnostics. `nmi_longest_ns` is writable through debugfs and controls slow-handler warnings. Sysctl-exposed panic knobs are registered from setup code, not here.

## Dependencies And Integration
Depends on APIC/NMI vector entry code, `x86_platform.get_nmi_reason()`, machine-check and microcode NMI hooks, SEV-ES IST hooks, irqentry, debug registers, tracepoint `trace_nmi_handler`, KVM exports, crash IPI callback code in `reboot.c`, and debugfs. NMI handlers are consumed by perf, watchdog, kdump, and selftests.

## Risks And Test Signals
Risks center on NMI-context safety: no sleeping locks, careful RCU use, preserving CR2/DR7, preventing list corruption during unregister, and avoiding false unknown-NMI panics. Back-to-back swallowing can hide a real unknown NMI by design. Test signals include `CONFIG_NMI_CHECK_CPU` stall diagnostics, handler duration tracepoints, NMI selftest coverage, crash dump shootdown behavior, and boot/runtime logs for unknown or external NMI paths.
