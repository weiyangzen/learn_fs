
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kvm_emul.S

Purpose: assembly template library copied and patched by `kvm.c` to emulate selected privileged instructions using KVM's magic page while preserving register state and interrupt semantics.

Important APIs/types/functions: exported template ranges `kvm_template_start/end`, `kvm_emulate_mtmsrd`, `kvm_emulate_mtmsr`, BookE `kvm_emulate_wrtee`, `kvm_emulate_wrteei_0`, Book3S 32-bit `kvm_emulate_mtsrin`, per-template offset symbols such as `*_branch_offs`, `*_reg_offs`, `*_orig_ins_offs`, length symbols, and the `kvm_tmp` 64 KiB allocation area.

Control flow: `SCRATCH_SAVE` marks the magic-page critical section with the current stack pointer and saves r30, r31, and CR fields. Templates read and update the magic-page MSR or segment-register fields, decide whether a real privileged instruction is still required, optionally execute the original instruction patched into the template, restore scratch state, and branch back to the instruction after the patched call site. `mtmsr/mtmsrd/wrtee` paths run the real instruction if critical MSR bits change or a pending interrupt must be delivered; otherwise they update the shared MSR field only.

State and persistence: templates are static text plus `kvm_tmp` scratch text space; runtime guest-visible state is the hypervisor shared page at `KVM_MAGIC_PAGE`, including MSR, interrupt-pending flag, scratch slots, and segment-register array.

Dependencies and integration: consumed by `kvm.c`, depends on `asm-offsets.h` offsets for `struct kvm_vcpu_arch_shared`, PowerPC register conventions, BookE/Book3S configuration guards, and the hypervisor honoring the critical-section field.

Risks: any mismatch between offset labels and C patching corrupts generated trampolines; scratch restore must run on every branch; magic-page critical markers assume r2 is never equal to r1; handling pending interrupts incorrectly can defer or spuriously enter the hypervisor.

Test signals: build all guarded variants, disassemble generated template copies, boot paravirt guests under interrupt load, and verify MSR[EE/RI] transitions, BookE `wrteei`, and Book3S `mtsrin` behavior.
