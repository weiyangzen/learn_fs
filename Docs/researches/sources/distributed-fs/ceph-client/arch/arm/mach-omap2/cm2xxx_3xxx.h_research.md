# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm2xxx_3xxx.h

Purpose: Provides CM register offsets and inline register accessors shared by OMAP2xxx and OMAP3xxx.

Important APIs/types/functions: Defines common offsets for FCLKEN, ICLKEN, IDLEST, AUTOIDLE, CLKSEL, and CLKSTCTRL registers. Provides inline `omap2_cm_read_mod_reg()`, `omap2_cm_write_mod_reg()`, `omap2_cm_rmw_mod_reg_bits()`, `omap2_cm_read_mod_bits_shift()`, `omap2_cm_set_mod_reg_bits()`, and `omap2_cm_clear_mod_reg_bits()`. Also defines shared GFX clock/status bit macros.

Control flow: Inline accessors compute `cm_base.va + module + idx`, perform relaxed MMIO reads/writes, and implement read-modify-write bit operations.

State and persistence: No independent state. Operations manipulate CM hardware registers directly through global `cm_base`.

Dependencies: Includes `cm.h` and Linux IO primitives outside assembler context.

Integration points: Used heavily by `cm2xxx.c`, `cm3xxx.c`, and related clock/PM code as the OMAP2/3 register access layer.

Risks: Callers are responsible for locking around read-modify-write. Bad module offsets or uninitialized `cm_base.va` can cause invalid MMIO. The header is not suitable for OMAP4+ CM layout.

Test signals: OMAP2/3 boot with successful CM mapping, module readiness polling, sleepdep/wkdep changes, and clock gating.
