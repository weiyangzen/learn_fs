# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_asm.h

Purpose: centralizes low-level PowerPC KVM assembly constants shared by BookE, Book3S PR, and Book3S HV entry/exit code. It gives assembly-safe load/store width macros, interrupt vector numbers, interrupt priority indexes, host flags, resume flags, guest-mode state values, and opcode masks used by KVM handlers.

Important APIs/types/functions: assembler macros `PPC_STD` and `PPC_LD` choose 64-bit `std`/`ld` or 32-bit high-word `stw`/`lwz` forms. `BOOKE_INTERRUPT_*` and `BOOK3S_INTERRUPT_*` encode trap vectors, including HV-specific vectors such as `BOOK3S_INTERRUPT_HV_DECREMENTER`, `BOOK3S_INTERRUPT_H_DATA_STORAGE`, and the real-mode passthrough sentinel `BOOK3S_INTERRUPT_HV_RM_HARD`. `BOOK3S_IRQPRIO_*`, `BOOK3S_HFLAG_*`, `RESUME_*`, and `KVM_GUEST_MODE_*` form the contract between assembly trampolines and C state machines. `PO_XOP_OPCODE_MASK` extracts major and extended opcodes.

Control flow: this header has no C control flow, but its constants drive guest exception dispatch. BookE and Book3S assembly handlers compare trap numbers against these definitions, prioritize pending Book3S interrupts using `BOOK3S_IRQPRIO_*`, and return to guest or host by testing `RESUME_*` flags.

State and persistence: no storage is allocated here. The values are ABI-like compile-time state baked into KVM assembly, `struct kvm_vcpu_arch` fields, and guest entry/exit paths. Changing them affects persistent binary compatibility between C, assembly, and generated offsets.

Dependencies and integration points: included by KVM Book3S and BookE handler headers and assembly. It integrates with exception vector layout, guest-mode tracking, resume-state handling, and instruction decode helpers.

Risks: vector values and guest-mode constants must stay synchronized with assembly labels and C switch paths. `VCPU_SIZE_BYTES` assumes a 64 KiB-aligned interrupt-vector page layout. The 32-bit `PPC_STD`/`PPC_LD` high-word behavior is subtle and can corrupt state if used with the wrong offset convention.

Test signals: build BookE and Book3S KVM configurations in 32-bit and 64-bit modes; boot guests that exercise decrementer, external, syscall, program, FP/Altivec/VSX, and HV fault exits; validate KVM tracepoints show expected `KVM_GUEST_MODE_*` transitions and resume paths.
