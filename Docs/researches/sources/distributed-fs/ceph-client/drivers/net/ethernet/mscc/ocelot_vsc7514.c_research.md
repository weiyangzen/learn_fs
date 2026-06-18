# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_vsc7514.c

Purpose: platform driver for the VSC7514 Ocelot switch. It binds the device-tree compatible `mscc,vsc7514-switch`, maps hardware targets, initializes the common Ocelot core, creates ports/devlink objects, enables optional FDMA/PTP support, and registers switchdev/netdevice notifiers.

Important APIs/functions: `ocelot_chip_init` selects `vsc7514_regmap`, initializes regfields, PLL, ops, MAC seed, and MACT sizing. IRQ handlers are `ocelot_xtr_irq_handler` for CPU-frame extraction and `ocelot_ptp_rdy_irq_handler` for TX timestamp readiness. `mscc_ocelot_init_ports` maps per-port resources, initializes physical or unused devlink ports, and calls `ocelot_probe_port`. `mscc_ocelot_probe` is the main bring-up path; `mscc_ocelot_remove` unwinds it.

Control flow: probe allocates a devlink-private `struct ocelot`, maps named IO targets (`sys`, `rew`, `qsys`, `ana`, `qs`, `s0`, `s1`, `s2`, plus optional `ptp` and `fdma`), resolves HSIO syscon, initializes chip state, requests extraction and optional PTP IRQs, parses `ethernet-ports`, assigns VCAP props and policer range, calls `ocelot_init`, probes ports, starts FDMA, registers shared-buffer devlink resources, optionally initializes timestamping, registers switchdev notifiers, then registers devlink. Remove reverses FDMA, devlink, timestamp, shared-buffer, port, notifier, and devlink allocation state.

State and persistence: runtime state lives under `struct ocelot`: target regmaps, per-port pointers, devlink ports, VCAP properties, policer base/max, FDMA/PTP flags, and notifier registration. No persistent disk state; all hardware configuration is reconstructed on probe.

Dependencies and integration: depends on platform resources, OF graph children, `vsc7514_regs.c` exports, Ocelot core APIs, phylink/netdevice/switchdev/devlink, optional FDMA, and PTP clock operations.

Risks: probe error unwinding spans many subsystems; missed teardown can leak devlink ports or registered netdevices. Optional target handling must leave `PTP`/`FDMA` null safely. `ocelot_xtr_irq_handler` must drain CPU queues on frame extraction errors to prevent interrupt storms or stuck RX state.

Test signals: device-tree probe on VSC7514 hardware or emulation, invalid/missing port resources, FDMA absent/present, PTP absent/present, frame extraction IRQ delivery, devlink port inventory, switchdev bridge operations, and clean module/platform removal.
