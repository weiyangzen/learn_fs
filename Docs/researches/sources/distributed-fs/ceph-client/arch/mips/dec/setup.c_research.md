# sources/distributed-fs/ceph-client/arch/mips/dec/setup.c

Purpose: central DECstation platform setup, especially interrupt routing, bus-error hook selection, write-buffer flushing, reboot hooks, and resource reservation.

Important APIs and state: exports `dec_kn_slot_base`, `dec_kn_slot_size`, `ioasic_ssr_lock`, `ioasic_base`, and `dec_interrupt[]`. Global priority tables `cpu_mask_nr_tbl` and `asic_mask_nr_tbl` are consumed by `int-handler.S`. `arch_init_irq()` selects per-model initialization and registers FPU, cascade, bus-error, and halt interrupts. `dec_irq_dispatch()` forwards selected IRQs to `do_IRQ()`.

Control flow: `plat_mem_setup()` installs bus-error init callback, write-buffer flush routine, reboot/power hooks, and reserves firmware working memory. Model-specific `dec_init_*()` functions copy IRQ route arrays and CPU/ASIC priority tables, then initialize CPU IRQs plus KN02 CSR or IOASIC IRQ chips as needed. `arch_init_irq()` selects the model path based on `mips_machtype`, adjusts FPU/halt routing for CPU features, and requests special interrupt lines.

State and persistence: route tables and `dec_interrupt[]` persist for all drivers. `busirq_handler` and flags are selected by `dec_be_init()`. Memblock reserves PROM working memory until later release.

Dependencies and integration: depends on PROM identification, DEC register headers, MIPS CPU IRQ core, IOASIC/KN02 IRQ chips, bus-error handlers, DS1287 time code, TurboChannel, and generic interrupt descriptors.

Risks and test signals: interrupt priority tables must align with assembly dispatcher expectations. Machine-type mistakes produce wrong IRQ maps. Test each supported DEC model class, verify `/proc/interrupts`, FPU exception/interrupt behavior, halt button, bus-error IRQ, and cascade routing.
