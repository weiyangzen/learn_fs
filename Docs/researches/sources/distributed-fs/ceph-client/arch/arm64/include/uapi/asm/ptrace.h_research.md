<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h` defines arm64 ptrace-visible processor state, PSR bits, syscall-emulation requests, MTE tag ptrace requests, SVE ptrace layout macros, and user register structures. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_PTRACE_H`, `PSR_MODE_EL0t`, `PSR_MODE_EL1t`, `PSR_MODE_EL1h`, `PSR_MODE_EL2t`, `PSR_MODE_EL2h`, `PSR_MODE_EL3t`, `PSR_MODE_EL3h`, `PSR_MODE_MASK`, `PSR_MODE32_BIT`, `PSR_F_BIT`, `PSR_I_BIT`, `PSR_A_BIT`, `PSR_D_BIT`, `PSR_BTYPE_MASK`, `PSR_SSBS_BIT`, `PSR_PAN_BIT`, `PSR_UAO_BIT`, `PSR_DIT_BIT`, `PSR_TCO_BIT`, `PSR_V_BIT`, `PSR_C_BIT`, `PSR_Z_BIT`, `PSR_N_BIT`, `PSR_BTYPE_SHIFT`, `PSR_f`, `PSR_s`, `PSR_x`, and 40 more; types: `user_pt_regs`, `user_fpsimd_state`, `user_hwdebug_state`, `user_sve_header`, `user_pac_mask`, `user_pac_address_keys`, `user_pac_generic_keys`, `user_za_header`, `user_gcs`. The file is 337 lines / 9799 bytes. Direct includes are `linux/types.h`, `asm/hwcap.h`, `asm/sve_context.h`.

### Control Flow
ptrace, signal, core-dump, perf, and debugger paths use these structures and constants to exchange register state with userspace.

### State, Persistence, And Dependencies
Register snapshots persist in ptrace stops, signal frames, core files, and perf samples. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Layout or flag mistakes break debuggers, crash dump tools, seccomp tracers, MTE tag inspection, or SVE vector-length handling.

### Test Signals
Run ptrace, gdb, seccomp, core-dump, SVE, and MTE tag selftests on native and compat processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ptrace.h -->
