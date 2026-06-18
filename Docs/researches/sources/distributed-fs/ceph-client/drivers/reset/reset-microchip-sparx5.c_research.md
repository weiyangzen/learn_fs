# sources/distributed-fs/ceph-client/drivers/reset/reset-microchip-sparx5.c

Purpose: Microchip Sparx5/LAN966x switch reset driver that performs a global switch-core reset early, then exposes a no-op reset controller.

Important APIs/types/functions: `struct reset_props`, `struct mchp_reset_context`, `sparx5_switch_reset()`, `mchp_lan966x_syscon_to_regmap()`, `mchp_sparx5_map_syscon()`, `mchp_sparx5_map_io()`, and `mchp_sparx5_reset_probe()`.

Control flow: probe maps CPU syscon and GCB registers, selects reset/protect offsets by compatible, protects the CPU core, writes the soft-reset bit, polls until hardware clears it, then registers one reset line whose `.reset` is a no-op. Driver registers at `postcore_initcall` for early reset.

State and persistence: hardware reset/protect registers are changed during probe; no later reset state is maintained.

Dependencies and integration: syscon/regmap, OF phandles, MMIO, reset framework, and special local syscon mapping for removable LAN966x PCI devices.

Risks and test signals: reset happens during probe, not consumer reset calls. Test early boot ordering, LAN966x removal-safe mapping, timeout handling, and that consumers do not expect later reset pulses.
