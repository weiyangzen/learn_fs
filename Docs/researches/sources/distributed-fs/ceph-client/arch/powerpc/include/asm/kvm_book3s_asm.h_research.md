# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s_asm.h

Purpose: defines Book3S KVM assembly glue, XICS register offsets, SMT/subcore limits, split-core coordination state, host-state save areas, and shadow-vcpu state used by PR and HV entry/exit handlers.

Important APIs/types/functions: `XICS_XIRR`, `XICS_MFRR`, and `XICS_IPI` define interrupt-controller offsets. `MAX_SMT_THREADS` and `MAX_SUBCORES` size vcore and split-mode arrays. The assembler `DO_KVM` macro branches selected vectors to `kvmppc_trampoline_*` labels when `CONFIG_KVM_BOOK3S_HANDLER` is enabled. C-visible structures include `struct kvm_split_mode`, `struct kvmppc_host_state`, and `struct kvmppc_book3s_shadow_vcpu`.

Control flow: assembly exception prologues expand `DO_KVM` for supported Book3S traps and route guest exits through KVM trampolines. HV entry code saves host registers and per-thread state in the PACA `kvmppc_host_state`; PR code uses the shadow vcpu for volatile guest state not immediately committed to `struct kvm_vcpu`.

State and persistence: host-state fields persist across guest entry until exit restores host MSR, stack, TOC, HID5, XICS/XIVE state, PMU registers, PURR/SPURR/DSCR, and split-mode state. Shadow-vcpu fields hold guest GPRs, CR/XER/CTR/LR/PC, fault DAR/DSISR, last instruction, SLB/SR shadows, and FSCR.

Dependencies and integration points: depends on `kvm_asm.h` in assembler mode and on PACA/Book3S KVM code in C mode. It integrates with XICS/XIVE interrupt delivery, split-core scheduling, guest entry assembly, and save/restore code.

Risks: structure layout is consumed by assembly and generated offsets, so field reordering is high risk. The trampoline vector list must match supported exception handlers. Split-core arrays are bounded by architectural SMT/subcore limits.

Test signals: compile with `CONFIG_KVM_BOOK3S_HANDLER`, run Book3S guest entry/exit tests across interrupt vectors, validate PMU/XICS/XIVE save/restore after guest exits, and boot POWER8 split-core or SMT-heavy configurations where available.
