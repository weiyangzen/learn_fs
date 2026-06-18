# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/powernv.h

Purpose: This compact header declares PowerNV-only platform hooks for nest MMU PTCR setup, CPU hotplug LPCR programming, and transactional memory initialization, with no-op stubs outside `CONFIG_PPC_POWERNV`.

Important APIs/types/functions: Under `CONFIG_PPC_POWERNV`, it exports `powernv_set_nmmu_ptcr`, `pnv_program_cpu_hotplug_lpcr`, and `pnv_tm_init`. Without PowerNV support, `powernv_set_nmmu_ptcr` and `pnv_tm_init` become empty inline functions; `pnv_program_cpu_hotplug_lpcr` is only declared for the PowerNV case.

Control flow: PowerNV initialization or CPU hotplug code calls these hooks to configure platform-specific MMU and LPCR state, and TM setup code calls `pnv_tm_init`. Non-PowerNV builds compile call sites away for the no-op functions.

State and persistence: State is platform CPU/MMU register state rather than header-owned memory. PTCR/LPCR programming persists in processor/platform registers until changed during boot, hotplug, or reconfiguration.

Dependencies and integration points: It depends on `CONFIG_PPC_POWERNV` and integrates with PowerNV CPU bringup, nest MMU configuration, OPAL/platform initialization, and transactional memory setup.

Risks and test signals: Stubs can hide accidental calls on unsupported platforms, so call sites must have correct config guards when they need real effects. LPCR and PTCR values are low-level architectural state and mistakes can break translation or hotplug. Tests are PowerNV boot, CPU online/offline cycles, radix/hash MMU mode coverage, and TM feature initialization checks.
