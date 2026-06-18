<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h` declares arm64 exception-vector aliases and branch-history-buffer hardening vector selection. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VECTORS_H`, `EL1_VECTOR_BHB_LOOP`, `EL1_VECTOR_BHB_FW`, `EL1_VECTOR_BHB_CLEAR_INSN`, `TRAMP_VALIAS`; types: `arm64_bp_harden_el1_vectors`; functions/prototypes/exports: `arm64_get_bp_hardening_vector`. The file is 73 lines / 1785 bytes. Direct includes are `linux/bug.h`, `linux/percpu.h`, `asm/fixmap.h`.

### Control Flow
Exception entry and mitigation code select EL1 vector variants such as loop, firmware, or clear-instruction BHB hardening through `arm64_get_bp_hardening_vector`.

### State, Persistence, And Dependencies
State is per-CPU vector base selection and mitigation capability data owned by entry and CPU feature code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong vector alias arithmetic or mitigation choice can break exception entry or leave branch-history hardening incomplete.

### Test Signals
Boot with affected CPU errata configs, inspect vector mappings, run Spectre/BHB mitigation checks, and exercise exception entry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vectors.h -->
