<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h` defines the arm64 signal-frame ABI, including general registers, FPSIMD, ESR, extra context records, SVE/SME ZA/ZT, TPIDR2, FPMR, GCS, and vector-length layout macros. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_SIGCONTEXT_H`, `FPSIMD_MAGIC`, `ESR_MAGIC`, `POE_MAGIC`, `EXTRA_MAGIC`, `SVE_MAGIC`, `SVE_SIG_FLAG_SM`, `TPIDR2_MAGIC`, `FPMR_MAGIC`, `ZA_MAGIC`, `ZT_MAGIC`, `GCS_MAGIC`, `SVE_VQ_BYTES`, `SVE_VQ_MIN`, `SVE_VQ_MAX`, `SVE_VL_MIN`, `SVE_VL_MAX`, `SVE_NUM_ZREGS`, `SVE_NUM_PREGS`, `sve_vl_valid`, `sve_vq_from_vl`, `sve_vl_from_vq`, `SVE_SIG_ZREG_SIZE`, `SVE_SIG_PREG_SIZE`, `SVE_SIG_FFR_SIZE`, `SVE_SIG_REGS_OFFSET`, `SVE_SIG_ZREGS_OFFSET`, `SVE_SIG_ZREG_OFFSET`, and 16 more; types: `sigcontext`, `_aarch64_ctx`, `fpsimd_context`, `esr_context`, `poe_context`, `extra_context`, `sve_context`, `tpidr2_context`, `fpmr_context`, `za_context`, `zt_context`, `gcs_context`. The file is 358 lines / 11386 bytes. Direct includes are `linux/types.h`, `asm/sve_context.h`.

### Control Flow
Signal delivery writes these records to the user stack and sigreturn parses them to restore task state. Optional records are chained with `_aarch64_ctx` headers and may extend beyond the base reserved area.

### State, Persistence, And Dependencies
Notable global/static state symbols are `head`. Signal context persists on the userspace signal stack until the handler returns or the process inspects/modifies it. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Record sizing, alignment, or magic-number drift breaks signal return, debuggers, checkpoint/restore, SVE/SME state preservation, and forward compatibility.

### Test Signals
Run signal, sigaltstack, SVE/SME, ZA/ZT, GCS, FPSIMD, and checkpoint/restore tests with varying vector lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/sigcontext.h -->
