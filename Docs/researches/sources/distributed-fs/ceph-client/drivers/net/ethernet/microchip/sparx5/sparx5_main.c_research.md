# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_main.c

## Purpose
`sparx5_main.c` is the platform-driver entry point and top-level hardware bring-up file for the Microchip Sparx5 switch driver, with optional LAN969x match data support. It maps register targets, interprets device-tree port configuration, resets and initializes the switch core, configures the core clock and shared forwarding resources, creates per-port netdev/phylink state, starts major subsystems, and performs ordered teardown.

It also supplies the Sparx5-specific static target map, register table pointers, hardware constants, operation callbacks, Open Firmware match table, and module registration.

## Important APIs, Types, And Functions
The local `struct initial_port_config` is a staging record populated from device tree before netdev creation; it keeps `portno`, `device_node`, `sparx5_port_config`, and optional SerDes PHY. `struct sparx5_ram_config` pairs memory-init registers with the bit values that need to be asserted and later observed as cleared.

`sparx5_main_iomap[]` maps every Sparx5 register target to an offset within one of three platform memory resources. `sparx5_create_targets()` consumes this table and fills `sparx5->regs[target]` base pointers so `spx5_rd()`, `spx5_wr()`, and `spx5_rmw()` can address generated register macros uniformly.

Target/feature helpers:

- `is_sparx5()` returns true for native Sparx5 target chip IDs and false for LAN969x variants.
- `sparx5_init_features()` enables PSFP and PTP feature bits on supported Sparx5 and LAN969x IDs.
- `sparx5_has_feature()` tests a feature bit in `sparx5->features`.

Bring-up helpers:

- `sparx5_create_port()` allocates a netdev, initializes `struct sparx5_port` defaults, calls `sparx5_port_init()`, sets VLAN defaults, configures phylink capabilities based on port bandwidth and RGMII support, creates phylink, and attaches the OF node.
- `sparx5_init_ram()` asserts reset/init bits for key memories and counters, then polls up to ten 1-2 ms intervals for the bits to clear.
- `sparx5_init_switchcore()` force-initializes EACL policer state, conditionally initializes RAM if the core is not enabled, resets counters, and enables the switch core/queue system.
- `sparx5_init_coreclock()` chooses a supported core clock for the target, configures LCPLL for native Sparx5, updates `sparx5->coreclock`, and writes clock-period-dependent values into HSCH, policer, LRN autoage, SIO clock, TAS, and policer update registers.
- `sparx5_qlim_set()` and `qlim_wm()` configure QRES limits and XQS shared queue watermarks from target buffer size.
- `sparx5_frame_io_init()` prefers FDMA when an FDMA IRQ is usable and falls back to register-based extraction/injection through the XTR IRQ and manual injection mode.
- `sparx5_frame_io_deinit()` disables selected frame I/O IRQs and deinitializes FDMA when active.
- `sparx5_board_init()` optionally remaps SGPIO signal-detect lines to ports based on `microchip,sd-sgpio` device-tree properties.
- `sparx5_forwarding_init()` programs own UPSIDs, enables internal CPU ports, initializes forwarding and flood PGIDs, enables CPU copy for CPU/broadcast PGIDs, forces FCS update for injected frames, and applies queue limits.

Driver entry points:

- `mchp_sparx5_probe()` is the full probe sequence.
- `mchp_sparx5_remove()` tears subsystems down in reverse operational order.
- `mchp_sparx5_match[]` matches `"microchip,sparx5-switch"` to `sparx5_desc` and LAN969x-compatible strings to `lan969x_desc` when enabled.

Static exported data includes `sparx5_regs`, `sparx5_consts`, `sparx5_ops`, and `sparx5_desc`. `sparx5_ops` binds port classification, muxing, PTP IRQ handling, calendar calculation, FDMA init/deinit/poll/transmit, and scheduler helper callbacks.

## Control Flow
Probe starts by validating a device tree or platform data source, allocating `struct sparx5` with devm memory, saving platform driver data, initializing `tx_lock`, loading match data, setting the global `regs` pointer, and resetting the optional shared switch reset controller.

The probe then creates `debugfs_root`, locates the `ethernet-ports` child node, counts ports, and builds an array of `initial_port_config` records. Each available port node must supply `reg`, `phy-mode`, and `microchip,bandwidth`. Optional `microchip,sd-sgpio` enables board-level signal-detect remapping. Non-RGMII ports must provide a SerDes PHY. Defaults such as DAC media, SerDes reset, port mode, and power-down are staged before actual port creation.

After parsing ports, `sparx5_create_targets()` maps platform memory resources and fills target bases. Probe establishes a base MAC from OF or a random fallback, reads IRQs, reads chip ID, derives `target_ct`, initializes feature bits, initializes switch core RAM, and configures the core clock. It then creates each staged port, initializes PGIDs and VLANs, applies board and forwarding setup, initializes calendar/QoS/VCAP/MAC table/stats/frame I/O/PTP subsystems, registers netdevs, and finally registers notifier blocks.

Error handling uses goto labels to unwind only the subsystems that have been initialized so far: unregister netdevs, PTP, frame I/O, stats, MAC table, VCAP, netdev destruction, config allocation, and the OF ports node. Successful probe jumps to `cleanup_config`, freeing the temporary config array and dropping the OF node reference while leaving persistent driver state active.

Remove removes debugfs, unregisters notifiers and netdevs, then deinitializes PTP, frame I/O, stats, MAC table, VCAP, and netdevs.

## State And Persistence Behavior
The central persistent runtime object is `struct sparx5`, owned by the platform device and allocated with devm memory. It stores register mappings, chip ID, target type, feature bits, ports, locks, per-subsystem workqueues, notifier blocks, frame I/O state, PTP state, VCAP state, PGID map, mirror entries, and match data.

Hardware state is initialized in an ordered sequence: switch memories and counters, core/clock, port hardware, PGIDs/VLANs/forwarding, scheduling/QoS/VCAP/MACT/statistics, frame I/O, and PTP. Many values survive as switch register state until reset or driver removal, while software state is volatile and recreated on probe.

Temporary device-tree parse state is allocated with `kzalloc_objs()` and freed before returning from probe. Port OF node references are kept in `sparx5_port::of_node`; the loop uses `for_each_available_child_of_node()`, and explicit `of_node_put()` appears in the SerDes error path and for the parent ports node.

The file initializes `tx_lock` early. Other locks and lists are initialized by subsystem-specific init functions, for example MAC table and stats code. `debugfs_root` is removed in `remove()`, but if probe fails after creating it and before successful bind, the failure path shown here does not explicitly remove it.

## Dependencies And Integration Points
The file depends heavily on generated register metadata from `sparx5_main_regs.h` and the register access helpers declared in `sparx5_main.h`. It includes subsystem headers for port, QoS, VCAP, and LAN969x match data. It integrates with the Linux platform bus, OF device-tree parsing, reset controller framework, phylink, PHY/SerDes, IRQ registration, debugfs, switchdev, netdev registration, and kernel module infrastructure.

Subsystem integration points are explicit in probe: `sparx5_pgid_init()`, `sparx5_vlan_init()`, `sparx5_calendar_init()`, `sparx5_qos_init()`, `sparx5_vcap_init()`, `sparx5_mact_init()`, `sparx5_stats_init()`, `sparx5_frame_io_init()`, `sparx5_ptp_init()`, `sparx5_register_netdevs()`, and `sparx5_register_notifier_blocks()`. `sparx5_forwarding_init()` uses PGID and internal-port helpers and prepares CPU ports for packet I/O. `sparx5_frame_io_init()` delegates to FDMA ops supplied by match data and falls back to packet register I/O helpers.

`sparx5_desc` supplies native Sparx5 `iomap`, register tables, constants, and ops. The OF table allows the same platform driver to bind native Sparx5 and, when configured, LAN969x devices with their own match data.

## Risks
The global `const struct sparx5_regs *regs` is set from the probed device match data. If multiple variants could be probed simultaneously, generated register helpers or users of this global need review for cross-device assumptions. `sparx5_create_targets()` assumes the iomap is ordered by range so `range_id[]` is initialized as expected; malformed match data could leave range indexing fragile. `IO_RANGES` is fixed at three, while match data also provides `ioranges`, so variants with more ranges would need code changes.

Probe failure after `debugfs_create_dir()` does not visibly remove `debugfs_root` on all error paths. `sparx5_create_port()` sets `sparx5->ports[portno]` before `sparx5_port_init()` and phylink creation complete; unwind through `sparx5_destroy_netdevs()` must tolerate partially initialized ports. Device-tree parse errors for individual ports often log and `continue`, which can reduce initialized port count without failing the whole probe unless later stages depend on those configs.

Frame I/O fallback mutates IRQ fields to `-ENXIO` on failure; later deinit depends on those sentinels. Core-clock support differs by target, so tests must catch invalid clock combinations. The remove path assumes all listed subsystems were initialized on successful probe; any future optional subsystem must preserve this ordering.

## Test Signals
Probe tests should cover native Sparx5 and LAN969x match data, missing or malformed `ethernet-ports`, missing `phy-mode`/bandwidth, RGMII ports without SerDes, non-RGMII ports with missing SerDes, absent base MAC, unavailable FDMA IRQ with XTR fallback, and FDMA success. Hardware bring-up signals include memory initialization timeout logs, core-clock register programming, PGID/flood mask state, CPU port enablement, netdev registration, PTP init, notifier registration, and clean removal. Failure-injection tests should target allocation failures, phylink creation failures, IRQ request failures, VCAP/MACT/stats/PTP init failures, and confirm that each goto label unwinds only initialized resources.
