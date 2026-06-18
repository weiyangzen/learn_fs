# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-54xx.h

Purpose: Defines OMAP54xx CM register masks and shifts for DPLL, clock selection, optional clocks, and static dependency fields.

Important APIs/types/functions: Provides DPLL masks, clock select/divider shifts, optional functional clock gate shifts, and STATDEP shifts for IPU, DSP, IVA, ABE, EMIF, L3MAIN, L3INIT, DSS, GPU, L4CFG, L4PER, L4SEC, and WKUPAON.

Control flow: No executable flow. OMAP54xx clockdomain data uses these macros in dependency bits and CM-related code uses the clock field masks.

State and persistence: No software state; documents generated hardware field layout.

Dependencies: Standalone guarded generated header used by OMAP5/54xx CM data.

Integration points: Supports OMAP54xx clockdomain static dependency programming and clock/DPLL configuration.

Risks: The header contains many generated masks with narrow hardware meanings. Manual edits risk desynchronizing from hardware databases and breaking clock tree or dependency behavior.

Test signals: OMAP5 builds, DPLL/clock selection tests, and runtime PM coverage for IPU/DSP/IVA/GPU/DSS/L3INIT domains.
