# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-8xxx.c

## Purpose

This file is the device-specific QCA8K DSA driver for QCA8327/QCA8328/QCA8334/QCA8337 switches. It implements register transport over MDIO and optional QCA management Ethernet packets, internal PHY MDIO access, device-tree parsing for CPU ports and power/LED settings, phylink and PCS handling, switch setup, management-packet MIB acceleration, probe/remove/shutdown, and suspend/resume.

## Important APIs, Types, and Functions

- `qca8k_split_addr()`, `qca8k_set_page()`, `qca8k_read_mii()`, and `qca8k_write_mii()` implement paged 32-bit register access over the MDIO bus.
- `qca8k_alloc_mdio_header()`, `qca8k_read_eth()`, `qca8k_write_eth()`, and `qca8k_rw_reg_ack_handler()` implement register reads/writes through QCA tagged management Ethernet frames when a CPU-port-0 conduit is operational.
- `qca8k_phy_eth_command()`, `qca8k_mdio_read()`, and `qca8k_mdio_write()` access internal PHY registers through the switch MDIO master, using Ethernet management first and falling back to MDIO.
- `qca8k_mdio_register()` and `qca8k_setup_mdio_bus()` register the internal/user MDIO bus and reject mixed internal/external PHY configurations.
- `qca8k_parse_port_config()`, `qca8k_mac_config_setup_internal_delay()`, `qca8k_phylink_mac_config()`, and `qca8k_pcs_config()` configure RGMII/SGMII delays, PLL, clock edge, SerDes mode, and PCS behavior.
- `qca8k_setup()` is the main DSA setup routine.
- `qca8k_switch_ops` wires common QCA8K DSA callbacks from `qca8k-common.c` plus local phylink, tagger, conduit, and LAG-related callbacks.
- `qca8k_sw_probe()`, `qca8k_sw_remove()`, `qca8k_sw_shutdown()`, `qca8k_suspend()`, and `qca8k_resume()` implement MDIO driver lifecycle and PM.
- `qca8327`, `qca8328`, and `qca833x` provide match data for device IDs, package mode, MIB count, and optional Ethernet MIB operations.

## Control Flow

Probe allocates `qca8k_priv`, stores the parent MDIO bus and OF match data, toggles optional reset GPIO, creates a no-cache regmap using custom bulk read/write/update callbacks, initializes the MDIO page cache to invalid, reads and validates the switch ID, allocates `dsa_switch`, initializes management and MIB completions/mutexes, fills DSA ops/phylink ops, initializes `reg_mutex`, stores drvdata, and registers the switch.

The regmap read/write path tries Ethernet management access when `priv->mgmt_conduit` is available, then falls back to paged MDIO. Management Ethernet packets are QCA-tagged frames with sequence numbers and completions; ACK handlers are installed through `qca8k_connect_tag_protocol()`. Internal PHY reads/writes similarly prefer Ethernet management command packets and fall back to MDIO master register access.

DSA setup finds a CPU port (0 preferred, 6 fallback), parses CPU-port RGMII/SGMII delay and clock settings, configures the internal MDIO bus, applies PWS and SoC-specific MAC power selection, registers LED class devices, initializes PCS objects, disables MAC06 exchange, enables CPU forwarding, initializes MIB counters, disables forwarding and user MACs by default, enables QCA header mode on CPU ports, routes unknown/broadcast/multicast/IGMP frames to the selected CPU port, programs CPU and user port membership, applies QCA8337 HOL fixups and QCA8327 flow-control thresholds, sets default max frame size, flushes FDB, and publishes ageing/LAG limits.

Phylink setup advertises RGMII/SGMII capabilities on CPU ports 0/6 and internal PHY modes on user ports. Link-up writes the port status register with speed, duplex, pause, and MAC enable bits unless in-band negotiation is used. PCS polling reads `QCA8K_REG_PORT_STATUS`; PCS config controls SerDes auto-negotiation, SGMII mode, PLL, delays, and clock edge bits.

## State and Persistence

Runtime state lives in `struct qca8k_priv`: switch ID/revision, mirror flags, LAG hash mode, enabled-port bitmap, isolation bitmap, parsed port delays, regmap, buses, DSA switch pointer, management conduit, Ethernet management sequence/ack/completion buffers, MIB autocast state, MDIO page cache, PCS objects, and LED objects. Hardware state includes CPU forwarding, port member masks, VLAN defaults, header mode, HOL thresholds, PWS settings, MIB enablement, SGMII/RGMII pad controls, and FDB contents. Suspend/resume uses `port_enabled_map` to disable and later re-enable only ports that were active before suspend.

## Dependencies and Integration Points

The driver depends on Linux DSA, phylink/PCS, MDIO, OF, GPIO reset, regmap, QCA tagger metadata from `linux/dsa/tag_qca.h`, netdevice management packet delivery, LED support through `qca8k_leds.h`, and shared QCA8K common functions. It integrates with compatible strings `qca,qca8327`, `qca,qca8328`, `qca,qca8334`, and `qca,qca8337`.

## Risks and Edge Cases

The transport path is complex: Ethernet management and MDIO access share sequence numbers, completions, mutexes, and fallback behavior. `qca8k_bulk_read()` and write paths rely on `mgmt_conduit` state being changed under the same management mutexes. Mixed internal and external PHY configurations are rejected because enabling MDIO master disconnects external MDC passthrough. CPU port 0 is required for Ethernet management acceleration. SGMII PLL and delay settings have chip/revision-specific warnings and restrictions. The QCA8337 HOL fixup and QCA8327 flow-control thresholds are hardware-workaround sensitive. In `qca8k_pcs_config()`, the final `ret` from clock-edge `qca8k_rmw()` is not returned, so that failure is not propagated.

## Test Signals

Strong signals are successful probe and switch ID validation for each compatible, DSA registration with seven ports, working QCA tag protocol callbacks, traffic through CPU port 0 and/or 6, internal MDIO bus registration in both explicit and legacy modes, rejection of mixed internal/external PHY DT layouts, RGMII/SGMII link-up with correct delays, management Ethernet read/write fallback behavior, MIB autocast stats, LED registration when enabled, VLAN/FDB/bridge/LAG behavior through common ops, suspend/resume preserving enabled ports, and clean remove/shutdown disabling ports.
