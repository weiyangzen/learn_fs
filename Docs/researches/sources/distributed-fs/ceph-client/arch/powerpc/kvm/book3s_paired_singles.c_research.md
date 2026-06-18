# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_paired_singles.c

Purpose: this file emulates paired-single and selected floating-point instructions for Book3S guests where paired-single behavior is required but not executed natively. It supports Gekko/Broadway-style paired-single load/store and arithmetic using FPR plus QPR state.

Important APIs: `kvmppc_emulate_paired_single()` is the exported emulator. Helpers include `kvmppc_inst_is_paired_single()` for opcode recognition, `kvmppc_emulate_fpr_load/store()` for ordinary FPR memory operations, `kvmppc_emulate_psq_load/store()` for paired-single quantized load/store forms, and `kvmppc_ps_one_in()`, `kvmppc_ps_two_in()`, `kvmppc_ps_three_in()` for applying scalar/simd floating helpers to PS0/PS1 halves.

Control flow: the emulator fetches `last_inst`, decodes register fields, verifies paired-single support and FP enablement, gives up host FP ownership, enables kernel FP, dispatches on primary opcode and extended fields, and returns an emulation result. Memory operations use `kvmppc_ld()`/`kvmppc_st()` and either inject data-storage faults or route MMIO through KVM load/store helpers. Arithmetic delegates to `fps_*` and `fpd_*` helpers while maintaining `vcpu->arch.qpr[]` as the second single component. Update forms write back RA after successful memory emulation.

State and persistence: state lives in guest FPRs, `vcpu->arch.qpr[]`, `vcpu->arch.fp.fpscr`, GPR RA writeback, CR for record forms, `paddr_accessed`, DAR/DSISR on injected faults, and queued Book3S interrupts. No global state is maintained.

Dependencies and integration: this file depends on KVM instruction fetch, Book3S interrupt queuing, KVM MMIO emulation, FP conversion helpers, and kernel FP enable/disable primitives. It is reached from PR exit handling when paired-single guests trap through FP unavailable/program paths.

Risks: implementation is incomplete for several comparison/FPSCR forms marked `XXX` or returning `EMULATE_FAIL`. Quantization type and scale fields are decoded but not fully applied, which matters for exact paired-single semantics. CR update code for comparisons appears suspect because it computes `tmp_cr` but folds from `cr` rather than `tmp_cr`. Kernel FP preemption boundaries must stay correct.

Test signals: run paired-single instruction suites for PSQ load/store update/indexed forms, arithmetic scalar variants, FPR load/store MMIO paths, disabled MSR[FP], page faults, and record forms. Compare against native hardware where possible, especially FPSCR/CR and quantized memory behavior.
