<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spram.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/spram.h

Purpose: Declares or stubs the MIPS scratchpad RAM configuration hook.

Important APIs/types/functions: `spram_config()` extern when `CONFIG_MIPS_SPRAM` is enabled; otherwise an inline no-op `spram_config()`.

Control flow: Platform or CPU setup calls `spram_config`; SPRAM-enabled builds run the real configuration routine, while other builds compile to no operation.

State and persistence: State is CPU/platform scratchpad RAM configuration performed elsewhere. This header owns no state.

Dependencies and integration points: Depends on `CONFIG_MIPS_SPRAM` and the implementation file that provides `spram_config`.

Risks: Callers must not assume scratchpad RAM exists when the no-op stub is selected. Missing extern implementation breaks SPRAM builds.

Test signals: SPRAM-enabled defconfig builds and boot on SPRAM-capable MIPS CPUs are the relevant signals.

Source read size: 11 lines, 254 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spram.h -->
