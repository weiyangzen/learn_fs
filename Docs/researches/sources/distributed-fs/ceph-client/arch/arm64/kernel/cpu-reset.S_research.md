<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S` implements the low-level arm64 `cpu_soft_restart` assembly path used by kexec and restart flows. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
functions/prototypes/exports: `SYM_FUNC_END`, `cpu_soft_restart`. The file is 53 lines / 1391 bytes. Direct includes are `linux/linkage.h`, `linux/cfi_types.h`, `asm/assembler.h`, `asm/sysreg.h`, `asm/virt.h`.

### Control Flow
The function disables MMU-sensitive state, switches to the supplied reset context and entry address, and branches with arguments arranged in registers according to the arm64 calling convention and HVC restart expectations.

### State, Persistence, And Dependencies
It mutates CPU system-register/MMU state and transfers control; no normal kernel state is expected to persist on return. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong register preservation, cache/MMU sequencing, or exception-level handling can hang restart/kexec or jump to an invalid physical address.

### Test Signals
Run kexec/kdump reboot tests, inspect objdump output, and test restart from EL1/EL2-capable boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/cpu-reset.S -->
