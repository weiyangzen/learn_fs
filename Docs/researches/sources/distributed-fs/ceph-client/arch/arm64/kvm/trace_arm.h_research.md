<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_arm.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_arm.h

## Purpose
This trace header defines arm64 KVM tracepoints for guest entry/exit, faults, MMIO, cache maintenance traps, arch timer state, nested virtualization exceptions, and forwarded sysreg traps.

## Important APIs, Types, And Functions
- `TRACE_EVENT(kvm_entry)` records guest PC at entry.
- `TRACE_EVENT(kvm_exit)` records exception return code, ESR exception class, and PC.
- Fault/MMIO events include `kvm_guest_fault`, `kvm_access_fault`, `kvm_mmio_emulate`, and `kvm_mmio_nisv`.
- Interrupt/cache events include `kvm_irq_line`, `kvm_set_way_flush`, and `kvm_toggle_cache`.
- Timer events include `kvm_timer_update_irq`, `kvm_get_timer_map`, `kvm_timer_save_state`, `kvm_timer_restore_state`, `kvm_timer_hrtimer_expire`, and `kvm_timer_emulate`.
- Nested virtualization events include `kvm_nested_eret`, `kvm_inject_nested_exception`, and `kvm_forward_sysreg_trap`.

## Control Flow
KVM runtime code calls generated `trace_kvm_*` helpers at relevant points. Each event records fields in `TP_fast_assign()` and formats output with `TP_printk()`. The header sets `TRACE_SYSTEM` to `kvm`, then sets `TRACE_INCLUDE_FILE` to `trace_arm` before including `trace/define_trace.h`.

## State And Persistence Behavior
Trace events store transient samples in the kernel tracing buffers when enabled. They do not mutate KVM state. Field values are captured by value except pointer fields such as vCPU pointers in nested events.

## Dependencies And Integration Points
The file depends on `asm/kvm_emulate.h`, `kvm/arm_arch_timer.h`, and Linux tracepoint machinery. Symbol formatting relies on shared symbolic tables such as `kvm_arm_exception_type`, `kvm_arm_exception_class`, `kvm_mode_names`, and `kvm_exception_type_names`.

## Risks And Edge Cases
- Tracepoint field choices are ABI-like for tooling; renaming events or changing field meanings can break scripts.
- Some fields are derived, for example ESR class is zeroed for non-trap exits.
- Timer map tracepoints dereference timer context pointers and must tolerate absent optional direct/emulated timers.
- `kvm_forward_sysreg_trap` prints decoded sysreg fields from a raw encoding; bad encodings can still be traced but may be misleading.

## Test Signals
Enable tracefs events under `events/kvm/` and run guests that trigger entry/exit, MMIO faults, timers, nested exits, and sysreg forwarding. Kernel build with tracing enabled validates macro expansion and include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_arm.h -->
