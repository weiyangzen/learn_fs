# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm81xx.h

Purpose: Defines TI81xx CM module offsets and clockdomain register offsets for TI814x/TI816x.

Important APIs/types/functions: Provides common module offsets for ACTIVE, DEFAULT, ALWON, and SGX; TI816x IVAHD module offsets; and offsets for ALWON L3 slow/medium/fast, Ethernet, MMU, MMUCFG, MPU, GEM, IVAHD0-2, SGX, default L3 medium/slow, PCI, Ducati, and SATA clockdomains.

Control flow: No executable flow. TI81xx clockdomain data uses these constants as `cm_inst` and `clkdm_offs`.

State and persistence: No software state; hardware register offset definitions only.

Dependencies: Standalone guarded header.

Integration points: Used by `clockdomains81xx_data.c` with `am33xx_clkdm_operations`.

Risks: TI814x/TI816x share some offsets but not all domains. Wrong SoC use can access unavailable modules.

Test signals: TI814x/TI816x boot and runtime PM for ALWON, default, IVAHD, SGX, SATA, PCI, and Ethernet domains.
