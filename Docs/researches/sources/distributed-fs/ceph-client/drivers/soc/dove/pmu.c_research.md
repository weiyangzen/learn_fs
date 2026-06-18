# sources/distributed-fs/ceph-client/drivers/soc/dove/pmu.c

Purpose: Marvell Dove PMU support for power domains, optional reset controller, and a chained PMU interrupt controller. It supports both legacy platform initialization and device-tree based initialization.

Important APIs and functions: reset ops `pmu_reset_reset()`, `pmu_reset_assert()`, and `pmu_reset_deassert()` manipulate `PMC_SW_RST`. `pmu_domain_power_on()` and `pmu_domain_power_off()` implement generic PM domain transitions using `PMU_PWR`, `PMU_ISO`, and reset masks. `dove_init_pmu_irq()` creates a linear IRQ domain and generic chip. `dove_init_pmu_legacy()` consumes board-provided initdata, while `dove_init_pmu()` parses `marvell,dove-pmu` and `domains` OF children.

Control flow: initialization maps PMU/PMC bases, registers reset support if configured, creates each power domain, parses reset references to derive reset masks, then optionally installs the chained interrupt handler. Power-off enables isolation, asserts reset, and sets power-down bits; power-on clears power-down, releases reset, and disables isolation.

State and persistence: `struct pmu_data` persists MMIO bases, lock, irq domain/generic chip, and reset controller state. Each `struct pmu_domain` stores masks and generic PM domain state. Hardware PMU/PMC registers persist the actual power/reset/isolation state.

Dependencies and integration: integrates with reset controller framework, generic PM domains, OF power-domain providers, IRQ domains/generic chips, and platform-specific `linux/soc/dove/pmu.h` legacy data.

Risks and test signals: risks include the documented non-race-free PMU IRQ clear register, leaking allocated domains on partial failure, and misparsed reset phandles when reset support is disabled. Test signals are power-domain attach/detach behavior, reset assertions, interrupt delivery through child IRQs, and legacy and DT boot coverage.
