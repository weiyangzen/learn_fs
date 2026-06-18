## sources/distributed-fs/ceph-client/arch/mips/kvm/trace.h

Purpose: Defines tracepoints and symbolic decoding tables for MIPS KVM transitions, exits, hardware register accesses, auxiliary FPU/MSA state changes, ASID/GuestID changes, and guest-mode state snapshots.

Important APIs, types, and functions: Trace events include `kvm_enter`, `kvm_reenter`, `kvm_out`, `kvm_exit`, `kvm_hwr`, `kvm_aux`, `kvm_asid_change`, `kvm_guestid_change`, and `kvm_guest_mode_change`. It declares `kvm_trace_guest_mode_change` plus registration hooks implemented in `mips.c`. Symbol tables map exit reasons, COP0/HWR operations, and auxiliary state operations to strings.

Control flow: Tracepoints capture fields from `struct kvm_vcpu` and COP0 accessors at call sites in the KVM backend. `TRACE_EVENT_FN(kvm_guest_mode_change, ...)` toggles a global flag through registration/unregistration callbacks, allowing expensive guest-mode-change tracing to be gated.

State and persistence: Trace events are transient kernel tracing records. Persistent state is limited to the global guest-mode-change trace enable flag.

Dependencies and integration points: Includes Linux tracepoint infrastructure and `trace/define_trace.h`. Used by `mips.c`, `emulate.c`, and auxiliary ownership paths. Exit reason constants align with MIPS Cause.ExcCode and VZ GuestCtl0.GExcCode values.

Risks: Symbolic constants must stay aligned with exit dispatch and VZ exception definitions or traces become misleading. Tracepoint field sizes use `unsigned long`, `u8`, and `u16`; ABI changes should preserve trace consumers. Guest-mode-change trace reads COP0 state and should remain gated to avoid overhead.

Test signals: Enable ftrace/perf events for guest enter/exit, MMIO/hardware register emulation, FPU/MSA ownership, ASID/GuestID rollover, and guest-mode-change registration; verify printed symbolic names match actual exit causes.
