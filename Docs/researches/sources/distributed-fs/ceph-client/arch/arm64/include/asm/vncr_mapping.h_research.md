<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h` documents byte offsets for virtualized nested control register state in the arm64 VNCR page. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ARM64_VNCR_MAPPING_H__`, `VNCR_VTTBR_EL2`, `VNCR_VTCR_EL2`, `VNCR_VMPIDR_EL2`, `VNCR_CNTVOFF_EL2`, `VNCR_HCR_EL2`, `VNCR_HSTR_EL2`, `VNCR_VPIDR_EL2`, `VNCR_TPIDR_EL2`, `VNCR_HCRX_EL2`, `VNCR_VNCR_EL2`, `VNCR_CPACR_EL1`, `VNCR_CONTEXTIDR_EL1`, `VNCR_SCTLR_EL1`, `VNCR_ACTLR_EL1`, `VNCR_TCR_EL1`, `VNCR_AFSR0_EL1`, `VNCR_AFSR1_EL1`, `VNCR_ESR_EL1`, `VNCR_MAIR_EL1`, `VNCR_AMAIR_EL1`, `VNCR_MDSCR_EL1`, `VNCR_SPSR_EL1`, `VNCR_CNTV_CVAL_EL0`, `VNCR_CNTV_CTL_EL0`, `VNCR_CNTP_CVAL_EL0`, `VNCR_CNTP_CTL_EL0`, `VNCR_SCXTNUM_EL1`, and 77 more. The file is 115 lines / 4042 bytes. There are no direct C include dependencies in this file.

### Control Flow
KVM and nested-virtualization code use these constants to index saved EL1/EL2, timer, GIC, trace, MPAM, and feature-control registers in the VNCR memory page.

### State, Persistence, And Dependencies
The offsets define layout for in-memory virtual CPU state. The header itself stores nothing but must remain synchronized with KVM save/restore code. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Any offset drift corrupts guest register state, especially for nested virtualization, virtual timer, GIC list registers, or trace/MPAM state.

### Test Signals
Run KVM nested-virtualization selftests, compare layout against architecture documentation, and exercise save/restore across vCPU migration and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vncr_mapping.h -->
