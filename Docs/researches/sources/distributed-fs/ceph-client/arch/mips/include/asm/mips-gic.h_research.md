# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-gic.h

Purpose: MIPS Global Interrupt Controller register interface and local interrupt definitions. It is included via `mips-cps.h`.

Important APIs/types/functions: Exposes `mips_gic_base` and `mips_gic_present()`. Accessor macros generate shared, local VP, redirected, per-interrupt register, and bit-per-interrupt helpers. Register groups cover shared config/counter, polarity/trigger/dual-edge, wedge, masks/pending, interrupt-to-pin and interrupt-to-VP maps, local VP control/pending/mask/map/other/ident/compare, and EIC shadow sets. `enum mips_gic_local_interrupt` lists watchdog, compare, timer, performance counter, software interrupts, FDC, and count. `mips_gic_vx_map_reg()` maps enum order to map-register index. Externs return virqs for CP0 compare, perfcount, and FDC interrupts.

Control flow, state, and persistence: Inline bit accessors select 32-bit or 64-bit register lanes based on `mips_cm_is64`. Persistent state is interrupt routing, masks, pending bits, and counter/compare state in GIC hardware.

Dependencies and integration: Uses CPS accessors and Linux bitops. Integrates with irqchip code, clockevents, perf, FDC, SMP IPI/local interrupt routing, and EIC mode.

Risks and test signals: Bit-lane math, FDC map index special-casing, and redirected VP access are high-risk. Test shared IRQ polarity/trigger configuration, local timer/perf/FDC virqs, IPI/software interrupts, EIC shadow routing, and 32/64-bit GIC windows.
