<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mchp-eic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mchp-eic.c

### Purpose
`irq-mchp-eic.c` supports the Microchip SAMA7G5 external interrupt controller. It adapts two external lines to parent GIC SPIs, including polarity/level conversion, wake control, clock handling, and syscore suspend/resume.

### Important APIs, Types, And Functions
`struct mchp_eic` stores MMIO base, peripheral clock, hierarchy domain, parent SPI numbers, saved SCFG registers, and wake mask. `mchp_eic_probe()` creates the domain. `mchp_eic_domain_alloc()` translates two-cell child specs and allocates parent GIC SPIs. `mchp_eic_irq_set_type()` programs `SCFG` polarity/level bits and converts low/falling types to parent high/rising types.

### Control Flow
Probe allocates the singleton, maps registers, finds the parent domain, gets/enables `pclk`, disables both EIC lines, parses the two parent IRQ specs to capture SPI numbers, creates a two-entry hierarchy domain, and registers syscore PM. Mask/unmask update the EIC enable bit and parent state. Wake toggles parent wake and tracks `wakeup_source`. Suspend saves SCFG registers and disables the clock when no wake source is armed; resume re-enables the clock and restores SCFG.

### State, Persistence, And Dependencies
State is the global `eic`, saved per-line SCFG values, wake mask, clock state, and hierarchy domain. Dependencies include OF IRQ parsing, GIC three-cell bindings, common clock framework, irqchip hierarchy helpers, and syscore PM.

### Integration Points
The EIC is a small child irqdomain under the GIC. Board devices reference the EIC for external wake-capable interrupt lines while the driver forwards actual delivery through parent SPIs.

### Risks
Only two IRQs are supported. The global singleton prevents multiple EICs. `mchp_eic_irq_set_wake()` calls `irq_set_irq_wake()` but ignores its return value. Clock state during suspend depends on correct wake mask tracking.

### Test Signals
Check all four trigger types, parent type conversion, wake enable/disable and clock behavior across suspend, missing clock or parent domain errors, and correct parsing of both parent SPI entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mchp-eic.c -->
