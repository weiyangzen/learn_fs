# sources/distributed-fs/ceph-client/drivers/mfd/ab8500-core.c

Purpose: Core MFD driver for ST-Ericsson AB8500/AB8505/AB9540/AB8540 mixed-signal power-management chips. It provides PRCMU-backed register access through the ABX500 abstraction, hierarchical interrupt demultiplexing, variant-specific child device creation, chip/status sysfs diagnostics, and suspend safety checks.

Important APIs, types, and functions: `ab8500_probe()` is the platform probe. Register access is implemented by `ab8500_prcmu_read()`, `ab8500_prcmu_write()`, `ab8500_prcmu_write_masked()`, and exposed through `ab8500_ops` registered with `abx500_register_ops()`. IRQ handling uses `ab8500_irq_chip`, `ab8500_irq_init()`, `ab8500_hierarchical_irq()`, `ab8500_handle_hierarchical_latch()`, and `ab8500_handle_hierarchical_line()`. Variant child arrays include `ab8500_devs`, `ab9540_devs`, `ab8505_devs`, `ab8540_devs`, and battery-management cells.

Control flow: probe allocates state, gets the parent IRQ, sets PRCMU accessors, detects version/revision, selects IRQ offset tables and latch hierarchy size, reads switch-off/turn-on reasons, masks/clears interrupt latches, registers ABX500 ops, creates an IRQ domain, requests the threaded parent IRQ, adds variant MFD cells and battery-management cells, then creates sysfs attribute groups depending on variant/cut.

State and persistence: `struct ab8500` holds locks, mask arrays, old masks, IRQ domain, transfer counter, version/chip ID, and access callbacks. `transfer_ongoing` blocks suspend while register/IRQ bus transfers are active. Static turn-on status override state is protected by `on_stat_lock` and affects AB9540 status reporting.

Dependencies and integration: depends on platform devices from DB8500 PRCMU, ABX500 core APIs, irqdomain, MFD core, OF matching for children, power supply children, and PRCMU ABB read/write functions.

Risks: sysfs group creation can overwrite `ret` and ignore earlier optional failures; ABX500 ops are not removed in this file; hierarchical IRQ mapping has variant-specific offset fixups that are easy to regress; register access relies on parent/child device relationships; mask arrays and GPIO rising/falling pairing require accurate IRQ type setup.

Test signals: probe each supported variant/cut, validate PRCMU register access, child creation, sysfs attributes, switch/turn-on status decoding, IRQ domain mappings and GPIO edge behavior, suspend rejection during transfers, and cleanup behavior on probe failure after ABX500 ops registration.
