# sources/distributed-fs/ceph-client/arch/s390/include/asm/kvm_para.h

Purpose: This header implements the s390 guest-side KVM paravirtual hypercall ABI using DIAG 0x500.

Important APIs/types/functions: Macro families generate `__kvm_hypercall0..6()` and `kvm_hypercall0..6()` with register arguments: R1 for hypercall number, R2-R6 for args 1-5, R7 for arg 6, and R2 return. It also defines `kvm_para_available()`, `kvm_arch_para_features()`, `kvm_arch_para_hints()`, and `kvm_check_and_clear_guest_paused()`.

Control flow: A guest hypercall wrapper increments DIAG 0x500 statistics, loads the required registers, executes `diag 2,4,0x500`, and returns the value from R2.

State and persistence: No persistent state is stored here beyond diagnostic counters updated by `diag_stat_inc()`. Feature and hint queries currently report no assigned feature bits.

Dependencies and integration points: It depends on UAPI KVM paravirt definitions and `asm/diag.h`, integrating guest kernel code with KVM hypercall handling.

Risks and test signals: Register constraints and calling convention must match both guest ABI and KVM host decode. Tests should cover each argument count, unavailable/non-KVM behavior assumptions, diag statistics, and hypercall error returns.
