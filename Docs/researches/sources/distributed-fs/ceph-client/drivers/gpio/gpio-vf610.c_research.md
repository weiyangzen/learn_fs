<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-vf610.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-vf610.c

Purpose: supports Freescale/NXP VF610, i.MX7ULP, and i.MX8ULP GPIO/PORT blocks using generic GPIO data registers plus PORT interrupt configuration.

Important APIs, types, and functions: `struct fsl_gpio_soc_data` records whether a SoC has PDDR and dual register bases. `struct vf610_gpio_port` owns the generic gpio chip, PORT base, GPIO base, saved IRQ config per pin, optional clocks, and parent IRQ. IRQ callbacks include chained handler, ack, set_type, mask, unmask, and wake. Probe configures `gpio_generic_chip_config`.

Control flow: probe selects SoC data, handles legacy compatible combinations for dual-base mapping, maps PORT/GPIO resources, obtains the parent IRQ, enables optional `port` and `gpio` clocks with devm cleanup, initializes generic GPIO using PDIR/PDOR/PDDR as available, masks all pin interrupts by clearing PCRs, clears ISFR, wires a one-parent gpio IRQ chip, and registers the chip. IRQ set_type stores the PORT IRQC mode and switches Linux flow handler; unmask writes the stored IRQC to the pin PCR.

State and persistence behavior: GPIO data/direction live in GPIO registers. `irqc[32]` caches requested interrupt modes while masked. Clock enable state is managed by devm actions. No suspend register snapshot is included; IRQ chip flags handle wake/mask behavior during suspend.

Dependencies and integration points: depends on OF compatibles, optional clocks, pinctrl-backed generic GPIO, chained IRQs, irqchip wake flags, and platform MMIO resources.

Risks and test signals: masking writes zero to the whole PCR, which may clear pin configuration bits if pinctrl has not restored them separately. Dual-base compatible handling must match DT resource layouts. Test all compatible data paths, optional/deferred clocks, generic GPIO direction with/without PDDR, IRQ type mapping, wake enable/disable, initial interrupt masking, and pinctrl interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-vf610.c -->
