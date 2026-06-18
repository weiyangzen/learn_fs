<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/abi.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/abi.h

**Purpose:** Defines the per-ABI signal and vDSO operations table used by MIPS signal delivery.

**Important APIs/types/functions:** `struct mips_abi` holds `setup_frame`, `setup_rt_frame`, restart trampoline address, signal context offsets for FPU state, and a `struct mips_vdso_image *`.

**Control flow:** Signal code selects a `mips_abi` for the current task ABI and calls its frame builders.

**State, dependencies, integration:** Depends on signal, siginfo, pt_regs, and vDSO types. It integrates native and compat ABI signal layout code.

**Risks and test signals:** Offset mismatches corrupt user signal frames and restarts. Test signal delivery/return for o32, n32, n64, FPU-used and no-FPU tasks, and vDSO selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/abi.h -->
