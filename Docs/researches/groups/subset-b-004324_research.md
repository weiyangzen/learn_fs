# subset-b-004324 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.c

Purpose: exposes mv88e6xxx switch internals through DSA devlink parameters, resources, regions, and fixed ASIC information. It turns hardware ATU/VTU/STU/PVT/register state into low-level debug snapshots and exposes ATU hash selection where supported.

Important APIs/types/functions: `mv88e6xxx_devlink_param_get/set()`, `mv88e6xxx_setup_devlink_params()`, `mv88e6xxx_setup_devlink_resources()`, `mv88e6xxx_setup_devlink_regions_global()`, `mv88e6xxx_setup_devlink_regions_port()`, and `mv88e6xxx_devlink_info_get()` are the DSA-facing entry points. Snapshot helpers allocate raw arrays for global registers, per-port registers, ATU entries, VTU entries, STU entries, and PVT entries.

Control flow: setup registers one runtime driver parameter, an ATU resource tree with per-bin occupancy callbacks, and conditional global devlink regions. Snapshot callbacks lock the chip register bus, walk hardware operation interfaces, copy register values into allocated buffers, then hand those buffers to devlink with `kfree` destructors.

State and persistence: it does not own persistent state; it observes switch tables, PVT mapping, and registers that persist in hardware until reset or reconfiguration. Runtime state is stored in `chip->regions[]` and `chip->ports[port].region`.

Dependencies/integration: depends on DSA devlink wrappers, Global1/Global2 ATU/VTU/PVT helpers, port register access, `chip->fid_bitmap`, and capability helpers such as `mv88e6xxx_has_stu()`.

Risks: ATU region sizing uses `mv88e6xxx_num_databases()` but may hold more than one MAC per FID, so the snapshot buffer can be undersized if many entries exist in a database. Error paths must avoid leaking allocated snapshots while register lock is held. Snapshots are raw, generation-specific ABI-like debug data.

Test signals: `devlink resource show` should report ATU occupancy, `devlink region dump` should work for global/port/ATU/VTU/STU/PVT where supported, unsupported hash ops should return `-EOPNOTSUPP`, and teardown should destroy only created regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.h

Purpose: declares the mv88e6xxx devlink integration surface used by the main switch driver and DSA callbacks.

Important APIs/types/functions: prototypes cover devlink parameter setup/teardown, resource setup, parameter get/set, global and per-port region setup/teardown, and `mv88e6xxx_devlink_info_get()`.

Control flow: no executable flow. The header defines lifecycle ordering expectations: setup functions are called during switch initialization, teardown functions during unwind/remove, and parameter/info functions are called by DSA devlink dispatch.

State and persistence: no state is stored here. Implementations in `devlink.c` write runtime region pointers into `struct mv88e6xxx_chip` and per-port state.

Dependencies/integration: includes only the local include guard and relies on including translation units to have DSA/devlink types visible. It is a private driver header, not a stable external API.

Risks: prototypes must stay aligned with DSA hook signatures as kernel devlink APIs evolve. Missing includes are acceptable only while all consumers include DSA headers first.

Test signals: compile coverage is the main signal; setup/remove paths should link all declared functions and DSA hooks should receive expected return codes for unsupported operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.c

Purpose: implements common operations for the Marvell switch Global 1 register block: reset/readiness, PPU control, switch MAC, priority maps, monitor/CPU ports, RMU disabling, device numbering, and statistics capture/read/clear.

Important APIs/types/functions: `mv88e6xxx_g1_read/write/wait_bit/wait_mask()` are the base accessors. Chip-family operations include `mv88e6185_g1_reset()`, `mv88e6250_g1_reset()`, `mv88e6352_g1_reset()`, EEPROM-done waits, PPU enable/disable, max-frame setup, IP/IEEE priority map reset, CPU/PTP CPU destination selection, management reserved multicast programming, RMU disable, statistics snapshot/read/clear, and device-number programming.

Control flow: most functions are read-modify-write helpers around Global1 registers. Reset paths set reset bits, wait for InitReady, and optionally wait for PPU polling. Statistics capture writes a busy command, waits for completion, then reads two counter registers.

State and persistence: settings live in switch hardware registers and are reset by switch reset or EEPROM reload. Counter snapshots are transient hardware latches. The code does not maintain private software state except through hardware side effects.

Dependencies/integration: used through per-chip ops tables in `chip.c`, and relies on `global1.h` bit definitions, core MDIO accessors, and caller-side `mv88e6xxx_reg_lock()` serialization.

Risks: EEPROM done status clears on read, so polling must be sequenced immediately after reset/reload. Family-specific bit layouts make wrong ops-table selection harmful. `mv88e6xxx_g1_stats_read()` silently returns zero on errors.

Test signals: reset should reach InitReady on supported chips; PPU enable/disable should transition status; ethtool stats should be stable after snapshot; CPU/monitor port setup should deliver management/PTP frames to the CPU port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.h

Purpose: defines the Global 1 register map, bit masks, table operation encodings, ATU/VTU/STU data encodings, monitor-control constants, statistics op constants, and prototypes for Global1, ATU, VTU, STU, reset, PPU, priority, and statistics helpers.

Important APIs/types/functions: constants cover status, MAC registers, control, VTU operation/data, ATU control/operation/data/MAC, priority maps, monitor/MGMT control, control2, and stats registers. Prototypes export base accessors plus family-specific reset, EEPROM, PPU, frame-size, stats, monitor, RMU, ATU, VTU, STU, and IRQ helpers.

Control flow: no executable code. The header is the contract that lets ops tables select the correct implementation for each switch family.

State and persistence: described state is hardware-resident: ATU MAC/FID entries, VTU VLAN membership, STU state, counters, PPU status, and reset/configuration bits.

Dependencies/integration: includes `chip.h` for shared types and enum values. It is consumed by Global1 implementation files, devlink snapshots, PTP/management setup, and switchdev/bridge integration.

Risks: many register offsets are aliased by chip generation, such as MAC bytes versus ATU/VTU FID registers, so users must call the right helper in the right hardware context. Bitfield comments encode non-obvious FID packing.

Test signals: build coverage across enabled chip families, runtime ATU/VTU programming, bridge VLAN/STP behavior, statistics reads, and interrupt handling for ATU/VTU violations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_atu.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_atu.c

Purpose: implements Address Translation Unit operations for the switch forwarding database: aging configuration, hash selection, get-next iteration, load/purge, flush/move/remove, and ATU violation interrupt handling.

Important APIs/types/functions: exported functions include `mv88e6xxx_g1_atu_set_learn2all()`, `mv88e6xxx_g1_atu_set_age_time()`, `mv88e6165_g1_atu_get_hash/set_hash()`, `mv88e6xxx_g1_atu_getnext()`, `mv88e6xxx_g1_atu_loadpurge()`, `mv88e6xxx_g1_atu_flush()`, `mv88e6xxx_g1_atu_remove()`, and ATU problem IRQ setup/free. Private helpers pack FIDs across generation-specific registers and marshal `struct mv88e6xxx_atu_entry`.

Control flow: callers wait for the ATU busy bit, write MAC/data/FID context, issue an operation in `MV88E6XXX_G1_ATU_OP`, then wait for completion. Get-next writes the starting MAC only for the first invalid seed entry. Violation IRQ handling clears the violation latch, reads FID/data/MAC, updates per-port counters, traces, and may invoke MAB miss handling.

State and persistence: ATU entries and age/hash settings are hardware state. Per-port violation counters in `chip->ports[]` are runtime software state.

Dependencies/integration: used by bridge/FDB/switchdev code, devlink ATU snapshots/resources, tracepoints, IRQ domains, and MAB handling in `switchdev.h`.

Risks: FID packing differs by database count, so boundary chips need coverage. `spid` is derived from entry state in violation records and is used for counters; member/miss paths assume valid port indexing more strongly than the full-violation path. Flush/move semantics depend on magic entry state values.

Test signals: FDB add/delete/dump across FIDs, age-time range checks, devlink ATU hash get/set, ATU full/member/miss violation tracepoints and counters, and MAB miss learning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_atu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_vtu.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_vtu.c

Purpose: implements VLAN Translation Unit and Spanning Tree Unit operations, including generation-specific VTU/STU data packing, get-next iteration, load/purge, flush, and VTU violation interrupt handling.

Important APIs/types/functions: exports generic and family-specific `*_vtu_getnext()`, `*_vtu_loadpurge()`, `mv88e6xxx_g1_vtu_flush()`, `*_stu_getnext()`, `*_stu_loadpurge()`, and VTU problem IRQ setup/free. Private helpers read/write FID, SID, VID valid/page bits, and 6185/6352 versus 6390 data layouts.

Control flow: VTU/STU operations wait for the busy bit, seed VID or SID only when starting from an invalid entry, issue a get-next/load-purge command, then read or write generation-specific data registers. VTU flush also clears `chip->fid_bitmap`. Violation IRQ handling reads and clears violation status, decodes SPID/VID, traces, and increments per-port counters.

State and persistence: VLAN membership, FID policy, SID mapping, and STP states are hardware table state. `chip->fid_bitmap` is software cache/state refreshed around VTU use.

Dependencies/integration: used by DSA bridge VLAN and STP paths, devlink VTU/STU snapshots, tracepoints, IRQ domains, and Global1 register definitions.

Risks: old and new chips pack membership/state differently; errors can create wrong VLAN membership or spanning-tree forwarding state. VID page handling extends VID encoding beyond 12 bits on some chips. IRQ paths index per-port counters from SPID without broad validation.

Test signals: bridge VLAN add/delete/dump, STP state changes, flush after VLAN teardown, devlink VTU/STU dumps, and synthetic or hardware VTU miss/member violation counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_vtu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.c

Purpose: implements Global 2 register operations for management frame routing, device/trunk/PVT tables, ingress-rate initialization, switch MAC, ATU statistics, priority override, EEPROM, SMI PHY proxying, watchdog handling, miscellaneous port-width mode, and nested interrupt domains.

Important APIs/types/functions: base accessors are `mv88e6xxx_g2_read/write/wait_bit()`. Exported helpers include management reserved-to-CPU setup, trunk/device/PVT table writes, EEPROM 8/16-bit get/set, Clause 22/45 SMI PHY accessors, watchdog ops structures, `mv88e6xxx_g2_irq_setup/free()`, MDIO IRQ mapping, and ATU stats get/set.

Control flow: command-style blocks wait for busy bits, write data/address registers, issue command words, then wait/read result registers. IRQ setup creates a 16-entry domain, maps nested interrupts, requests the Global1 device IRQ, and wires watchdog handling as a nested IRQ.

State and persistence: switch management/trunk/PVT/priority/EEPROM settings live in hardware. EEPROM content is persistent. Runtime state includes `chip->g2_irq`, `device_irq`, `watchdog_irq`, and MDIO bus IRQ assignments.

Dependencies/integration: used by devlink resources/PVT, PHY/MDIO code, watchdog ops tables, DSA multi-chip routing, ethtool EEPROM hooks, and Global1 device interrupt signaling.

Risks: EEPROM writes can persistently alter board configuration and 16-bit writes require write-enable. Watchdog action on newer chips may reset the switch. IRQ setup error unwind must dispose mappings consistently; watchdog request failure currently returns without disposing `watchdog_irq`.

Test signals: MDIO Clause 22/45 PHY reads, ethtool EEPROM odd/even offsets, PVT devlink dumps, trunk setup/clear, nested PHY/watchdog IRQs, watchdog reset recovery, and teardown after partial setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.h

Purpose: defines the Global 2 register map, command encodings, data masks, scratch/GPIO register selectors, interrupt bits, watchdog bits, AVB/PTP window constants, SMI PHY command fields, and public prototypes for Global2 helpers and ops structures.

Important APIs/types/functions: constants cover interrupt source/mask, management enable, device mapping, trunk tables, IRL commands, PVT, switch MAC, ATU stats, EEPROM, AVB command/data, SMI PHY command/data, scratch/misc, watchdog, QoS, and misc port-width mode. Prototypes export Global2 accessors, EEPROM, PVT, IRQ, MDIO IRQ, AVB/watchdog/GPIO ops, scratch SMI muxing, and ATU stats.

Control flow: no executable flow. The header centralizes hardware encodings used by `global2.c`, `global2_avb.c`, `global2_scratch.c`, `hwtstamp.c`, and PHY/PCS code.

State and persistence: describes both volatile register state and persistent EEPROM data. Scratch straps/config registers reflect board/chip configuration and may gate SerDes/SMI/GPIO behavior.

Dependencies/integration: includes `chip.h`; exported ops are selected by chip family tables and consumed by DSA switch setup, MDIO, PTP, GPIO, devlink, and watchdog paths.

Risks: multiple families overload the same offsets with different meanings, especially watchdog and AVB command encodings. Misusing field widths can address the wrong port or external/internal PHY bus.

Test signals: compile coverage, per-family smoke tests for EEPROM, AVB/PTP, SMI PHY, watchdog, scratch GPIO, and interrupt masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_avb.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_avb.c

Purpose: provides AVB/PTP/TAI register-window access operations through Global2 AVB command/data registers for several mv88e6xxx generations.

Important APIs/types/functions: private helpers `mv88e6xxx_g2_avb_read()` and `mv88e6xxx_g2_avb_write()` implement the busy-bit transaction. Exported ops tables are `mv88e6352_avb_ops`, `mv88e6165_avb_ops`, and `mv88e6390_avb_ops`, each supplying port PTP, global PTP, and TAI read/write callbacks.

Control flow: reads wait for idle, reject snapshots longer than four words, issue either single-read or incrementing-read command, wait again, then read data repeatedly. Writes wait for idle, write one data word, issue write command, and wait for completion. Family wrappers construct command words with generation-specific opcodes and special global port numbers.

State and persistence: accessed registers configure PTP/AVB/TAI hardware and may contain latched timestamp data. The file itself stores no runtime state.

Dependencies/integration: consumed by `hwtstamp.c` and PTP code through `chip->info->ops->avb_ops`; relies on Global2 register definitions and outer register-locking by callers.

Risks: hardware supports only four-word snapshots; callers must split larger reads. Similar-looking 6352 and 6390 command encodings use different op fields and global port numbers. No local locking is done.

Test signals: PTP setup should read/write global and per-port registers, RX/TX timestamp reads should fetch four-word blocks, 6165 TAI special port selection should work, and oversized reads should return `-E2BIG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_avb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_scratch.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_scratch.c

Purpose: implements Global2 scratch/misc indirect register access for GPIO control, external SMI pin muxing, and SerDes strap detection.

Important APIs/types/functions: private helpers `mv88e6xxx_g2_scratch_read/write()`, bit get/set helpers, GPIO callbacks for data/direction/pin-control, exported `mv88e6352_gpio_ops`, `mv88e6390_g2_scratch_gpio_set_smi()`, `mv88e6393x_g2_scratch_gpio_set_smi()`, and `mv88e6352_g2_scratch_port_has_serdes()`.

Control flow: scratch reads write the pointer then read back data; writes set update plus pointer/data. GPIO operations map pin offsets into paired scratch registers. SMI mux helpers inspect strap/config bits, account for inverted semantics on some chips, then set or clear `NORMALSMI`. SerDes detection reads strap data and reports whether port 4 or 5 owns the SerDes.

State and persistence: scratch registers reflect hardware straps and mutable GPIO/mux state. `chip->gpio_data[]` caches output data bytes so set operations preserve other pins.

Dependencies/integration: used by GPIO registration, MDIO external SMI setup, PCS initialization, and `global2.h` scratch constants. Callers are expected to hold register lock.

Risks: `mv88e6352_g2_scratch_gpio_set_pctl()` masks `func` before shifting using the shifted mask, which can drop function bits. SMI muxing can fail with `-EBUSY` when port 0 is strapped to conflicting modes. Cached GPIO output can diverge if hardware changes outside this driver.

Test signals: GPIO direction/data/pinmux operations, external SMI mux toggling on 6390/6393x, SerDes port detection for 6352, and preservation of neighboring GPIO bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global2_scratch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.c

Purpose: implements DSA hardware timestamping for mv88e6xxx PTP-capable switches, including ethtool timestamp capabilities, per-port hwtstamp configuration, RX/TX skb timestamp matching, and PTP hardware setup.

Important APIs/types/functions: DSA entry points are `mv88e6xxx_get_ts_info()`, `mv88e6xxx_port_hwtstamp_set/get()`, `mv88e6xxx_port_rxtstamp()`, `mv88e6xxx_port_txtstamp()`, `mv88e6xxx_hwtstamp_work()`, setup/free, and per-family global/port enable/disable helpers. Internal state is `struct mv88e6xxx_port_hwtstamp`, RX queues, `tx_skb`, sequence IDs, and state bits.

Control flow: configuration clears the enabled bit, validates tx/rx filters, updates global/port PTP hardware enable counts under the register lock, then enables data-path checks. RX path classifies PTP, queues skb in arrival0/arrival1 queue, and schedules PTP worker. Worker reads latched timestamp blocks, matches sequence IDs, converts raw cycles through `chip->tstamp_tc`, stamps skbs, and releases them. TX path clones one skb, waits for departure timestamp, validates status/sequence, completes or drops on timeout/error.

State and persistence: runtime state includes per-port queues, config, enabled/TX-in-progress bits, `enable_count`, cloned TX skb, and timecounter. Hardware timestamp latches are transient.

Dependencies/integration: depends on Global2 AVB ops, PTP clock worker, `ptp_classify_raw()`, DSA RX/TX hooks, and `ptp_ops` register metadata.

Risks: `enable_count` is decremented on every disable path and can underflow if disabling an already disabled port. Only one TX timestamp per port is supported; excess timestampable packets are ignored. RX hardware holds one timestamp per arrival register, so queued extras may be unstamped.

Test signals: `ethtool -T`, `SIOCSHWTSTAMP` filter validation, ptp4l L2/L4 event traffic, TX timeout recovery, sequence mismatch warnings, RX PDelay response path using arrival1, and 6341 MAC timestamp mode setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.h

Purpose: defines PTP/global/per-port timestamp register constants, timestamp status bits, and conditional declarations or stubs for mv88e6xxx hardware timestamping support.

Important APIs/types/functions: constants include PTP ethertype, message type masks, arrival pointer, global config bits, per-port PTP config registers, arrival/departure status/time/sequence registers, and timestamp valid/status masks. When `CONFIG_NET_DSA_MV88E6XXX_PTP` is enabled, it declares hwtstamp DSA hooks, worker/setup/free, and enable/disable helpers; otherwise it provides no-op or `-EOPNOTSUPP` stubs.

Control flow: no runtime flow in the header beyond inline stubs. It gates PTP functionality at compile time and lets non-PTP builds avoid conditional code at call sites.

State and persistence: describes transient hardware timestamp latches and configuration registers. Software state is declared elsewhere in `chip.h`.

Dependencies/integration: includes `chip.h` and is consumed by the main switch driver, PTP implementation, and `hwtstamp.c`.

Risks: spelling-compatible constant names include hardware typos such as departure/overwritten comments; consumers must use masks exactly. Stub behavior must remain consistent with DSA expectations for non-PTP builds.

Test signals: builds with and without `CONFIG_NET_DSA_MV88E6XXX_PTP`, `ethtool -T` returning support only when enabled, and PTP timestamp registers matching ops table register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/leds.c

Purpose: registers per-port LED class devices for supported mv88e6xxx ports and maps Linux LED brightness, blink, and `netdev` hardware-control rules onto switch LED selector registers.

Important APIs/types/functions: `mv88e6xxx_port_setup_leds()` parses firmware LED child nodes and registers LED classdevs. Helpers read/write the indirect port LED control register, force brightness, configure hardware blink periods, select hardware netdev trigger modes from `mv88e6352_led_hwconfigs`, and report supported/current rules.

Control flow: setup skips unsupported ports and missing firmware nodes, validates LED `reg` numbers 0/1, applies default state, fills classdev callbacks, constructs a device name, and registers via `devm_led_classdev_register_ext()`. Runtime callbacks take the switch register lock, read LED selector state, update only the relevant LED selector bits, and write back with the pointer/update bits.

State and persistence: LED mode lives in port hardware registers. Runtime classdev state is embedded in each `struct mv88e6xxx_port`. Firmware `default-state` can initialize hardware state during setup.

Dependencies/integration: depends on Linux LED classdev/netdev trigger APIs, firmware node APIs, DSA user device lookup, port register definitions, and the mv88e6xxx register lock.

Risks: the hardware-config table is marked MV88E6352-specific, so other families may be misrepresented if reused. Hardware blink supports only discrete periods; unsupported timing falls back to software. Only ports 0 through 5 are accepted.

Test signals: device-tree LED nodes should create LED devices, brightness on/off should force selectors, supported netdev trigger rules should program hardware selectors, unsupported rule combinations should return `-EOPNOTSUPP`, and blink period choices should match hardware values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-6185.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-6185.c

Purpose: provides a simple phylink PCS wrapper for fixed SERDES/1000BASE-X-capable ports on 88E6185-family switches.

Important APIs/types/functions: `struct mv88e6185_pcs` stores `phylink_pcs`, optional IRQ, chip, and port. The exported `mv88e6185_pcs_ops` supplies init, teardown, and select. Phylink callbacks read port status, no-op config, and no-op AN restart.

Control flow: init checks the port `cmode` for SERDES or 1000BASE-X, allocates PCS state, installs phylink ops, maps a SerDes IRQ if available, and otherwise enables polling. IRQ and state callbacks read `MV88E6XXX_PORT_STS`, decode link, speed, and duplex, and call `phylink_pcs_change()` on IRQ.

State and persistence: runtime state is the allocated PCS object stored in `chip->ports[port].pcs_private`. Hardware link state is read from the port status register.

Dependencies/integration: depends on phylink, port register definitions, SerDes IRQ mapping, and chip port `cmode` initialized elsewhere.

Risks: PCS configuration is intentionally no-op; wrong static `cmode` means no PCS gets registered. IRQ handler treats any successful status read as handled and does not validate speed beyond state decode.

Test signals: ports in SERDES/1000BASE-X mode should expose a PCS to phylink, link changes should be reported by IRQ or polling, and teardown should free IRQ and allocated state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-6185.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-6352.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-6352.c

Purpose: implements a Clause 22 fiber-page PCS for 88E6352-family SerDes, integrating with phylink for link state, in-band advertisement, power, fixed link-up configuration, and link-change IRQs.

Important APIs/types/functions: `struct marvell_c22_pcs` embeds an `mdio_device` and `phylink_pcs`. Shared helpers switch to the Marvell fiber page, restore the previous page, modify registers, power the PCS, control link-change IRQs, decode state, configure advertisement, restart AN, and set fixed speed/duplex. `mv88e6352_pcs_ops` exposes init/teardown/select.

Control flow: init first checks scratch straps via `mv88e6352_g2_scratch_port_has_serdes()`, allocates an MDIO-backed PCS at `MV88E6352_ADDR_SERDES`, installs optional IRQ/polling, and stores it per port. Runtime C22 operations lock the MDIO bus while changing pages and restore the old page before returning.

State and persistence: runtime state is allocated PCS plus IRQ. Hardware state includes C22 fiber-page BMCR/advertisement/interrupt registers.

Dependencies/integration: depends on default MDIO bus access, scratch SerDes detection, phylink C22 helpers, SerDes IRQ mapping, and port cmode link checks for auto-media port 4.

Risks: page-switch restore is critical; failed restore can break later PHY access. `marvell_c22_pcs_set_fiber_page()` returns without unlocking on read/write failure, which risks leaving the MDIO lock held. Only one SerDes address is assumed.

Test signals: SerDes strap detection, phylink state decode, in-band advertisement programming, IRQ versus polling mode, power down/up, page restore under error injection, and auto-media link_check behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-6352.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-639x.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-639x.c

Purpose: implements Clause 45 PCS support for 88E6390/6393x SerDes lanes, covering SGMII/1000BASE-X/2500BASE-X and high-speed 5G/10G/RXAUI/XAUI/USXGMII modes with phylink integration and hardware errata workarounds.

Important APIs/types/functions: `struct mv88e639x_pcs` owns one MDIO C45 endpoint plus separate SGMII and XG `phylink_pcs` objects. Shared helpers wrap C45 read/write/modify, IRQ dispatch, SGMII power/config/state, XG state, and PCS selection. Exported ops are `mv88e6390_pcs_ops` and `mv88e6393x_pcs_ops`.

Control flow: init maps a SerDes lane from port, allocates PCS, assigns family-specific phylink ops, applies required errata, requests optional IRQ, and stores private state. PCS selection returns SGMII or XG PCS by interface. Enable paths set active IRQ handler, unmask interrupts, power lanes, and post-config applies family errata before enabling links.

State and persistence: runtime state includes selected interface, `handle_irq`, IRQ number, erratum flags, 5G support, and PCS objects. Hardware state spans C45 PHYXS/VEND1 registers, power-down bits, advertisement, link status, and interrupt masks.

Dependencies/integration: depends on default MDIO bus, phylink, SerDes lane mapping, `phy.h`, port/serdes register constants, and family/product IDs.

Risks: complex errata sequences must be applied in the right power/config order. `handle_irq` is shared between SGMII and XG PCS, so active PCS transitions must disable the previous handler cleanly. 2500BASE-X AN workaround intentionally rewrites nonstandard vendor registers.

Test signals: phylink mode switches among SGMII/1000BASE-X/2500BASE-X/10G/USXGMII, link IRQs and polling fallback, erratum 3.14/4.6/4.8/5.2 register writes, 5G support gating, and teardown after IRQ setup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/pcs-639x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.c

Purpose: provides generic PHY register access wrappers and PHY Polling Unit coordination for mv88e6xxx internal PHYs.

Important APIs/types/functions: direct 6165 accessors call core `mv88e6xxx_read/write()`. Generic `mv88e6xxx_phy_read/write()` and C45 variants dispatch through chip ops and the default MDIO bus. Page helpers select a PHY page, read/write a register, and restore copper page. PPU helpers initialize/destroy mutex/timer/work state, disable PPU for direct register access, and re-enable it asynchronously.

Control flow: normal reads resolve the default MDIO bus and chip ops, returning `-EOPNOTSUPP` if absent. Paged reads/writes reject register 22 itself, switch page, perform access, and restore page. PPU-protected 6185 operations disable the PPU under `ppu_mutex`, perform raw access, then schedule re-enable after 10 ms via timer/work.

State and persistence: runtime state is `chip->ppu_mutex`, `ppu_timer`, `ppu_work`, and `ppu_disabled`. PHY register contents are hardware state; selected pages are restored to copper page after helper access.

Dependencies/integration: used by MDIO bus callbacks, PHY setup, and chip ops. Depends on module/MDIO APIs, timers/workqueues, and `phy.h` constants.

Risks: `mv88e6xxx_phy_page_write()` writes the page register twice before writing target register, which is redundant but benign if successful. PPU re-enable work uses `mutex_trylock`, so repeated contention can delay PPU restoration. Page restore errors are logged but cannot be recovered by caller.

Test signals: internal PHY C22/C45 reads through default MDIO bus, paged register access restoring copper page, PPU disable/re-enable around 6185 accesses, no-op PPU setup on chips without PPU ops, and teardown canceling timer/work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.h

Purpose: declares private mv88e6xxx PHY access helpers and defines the Marvell PHY page register constants used by internal PHY access code.

Important APIs/types/functions: constants are `MV88E6XXX_PHY_PAGE` and `MV88E6XXX_PHY_PAGE_COPPER`. Prototypes cover direct 6165 access, 6185 PPU-mediated access, generic C22 and C45 read/write, paged read/write, and PHY lifecycle/setup helpers.

Control flow: no executable flow. The header lets chip ops tables select direct, PPU-mediated, or Global2 SMI PHY access implementations while keeping callers on generic wrappers.

State and persistence: no state is stored here. Declared functions manipulate PHY hardware registers and runtime PPU coordination state in `struct mv88e6xxx_chip`.

Dependencies/integration: consumed by `phy.c`, `pcs-639x.c`, chip ops tables, and MDIO setup. It relies on visible declarations for `struct mv88e6xxx_chip` and `struct mii_bus`.

Risks: page register constant must not be used as a normal paged target register; implementation rejects that. Header guard comment has a minor formatting typo but no functional effect.

Test signals: compile/link coverage for all selected chip ops, MDIO bus callbacks using C22/C45 prototypes, and page helpers returning `-EINVAL` for register 22.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/phy.h -->
