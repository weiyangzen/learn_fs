# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k.h

## Purpose

This header defines the QCA8K driver contract: register offsets, bit fields, constants, command enums, private data structures, LED descriptors, MIB/FDB structures, helper inline mappings, and prototypes shared by `qca8k-8xxx.c`, `qca8k-common.c`, and optional LED support.

## Important APIs, Types, and Functions

- Hardware constants define ports, CPU ports, max MTU, LAG capacity, PHY IDs, switch IDs, MIB counts, FDB size, and timeouts.
- Register and bitfield macros cover global control, port pad controls, PWS, MIB, MDIO master, LED control, MAC power, EEE, trunk/LAG, VLAN/ATU/VTU lookup, port lookup, queue/HOL, packet editing, L3, MIB, and MII MMD access.
- Command enums model FDB (`qca8k_fdb_cmd`), VLAN (`qca8k_vlan_cmd`), and MIB (`qca8k_mid_cmd`) operations.
- `struct qca8k_match_data` stores device ID, package flag, MIB count, and optional info ops.
- `struct qca8k_mgmt_eth_data` and `struct qca8k_mib_eth_data` store management Ethernet command/MIB completion state.
- `struct qca8k_ports_config` stores parsed RGMII/SGMII delay and clock settings.
- `struct qca8k_priv` is the central runtime state for switch ID/revision, mirror/LAG/port maps, regmap, buses, DSA switch, locks, reset GPIO, management conduit, MDIO cache, PCS instances, and LED array.
- Function prototypes expose common setup, register, DSA, FDB/MDB/VLAN, mirror, bridge, MTU, ageing, and LAG helpers.

## Control Flow

This header has no runtime control flow, but it encodes the interfaces used by the QCA8K implementation. The flow across source files is: `qca8k-8xxx.c` owns probe/setup/transport/phylink and calls common functions declared here; `qca8k-common.c` implements most DSA switch operations; `qca8k-leds.c` consumes LED constants and `struct qca8k_priv` LED storage; `qca8k_leds.h` conditionally declares the LED setup entry point.

## State and Persistence

The header defines both software state and persistent hardware state accessors. `struct qca8k_priv` fields such as enabled ports, isolation, mirror masks, LAG hash mode, MDIO page cache, management sequence number, and PCS/LED objects persist for the driver instance lifetime. Register macros define hardware state that persists until reset or reconfiguration.

## Dependencies and Integration Points

It depends on Linux delay, regmap, GPIO consumer, LED class, and QCA DSA tag header definitions. The prototypes are consumed by QCA8K compilation units and DSA operations. It also embeds assumptions about Linux bridge, switchdev, phylink, MDIO, ethtool, and netdevice APIs through function signatures and struct fields.

## Risks and Edge Cases

Macro correctness is critical because many fields are programmed with `FIELD_PREP`/`FIELD_GET`. The typo `QCA8K_LED_BLINK_FREQ_SHITF` is present but appears unused in the read files; if used later, the misspelling may propagate. `QCA8K_LED_COUNT` excludes CPU ports by deriving from total ports minus CPU ports. `qca8k_port_to_phy()` assumes ports 1-5 map to PHYs 0-4 and is invalid for CPU ports. Struct fields such as `port_enabled_map` and `port_isolated_map` are 8-bit, adequate for seven ports but fragile if reused for larger switches.

## Test Signals

Compile coverage is the main signal: all QCA8K objects should agree on prototypes and constants. Runtime signals include correct register addressing for all DSA operations, correct per-chip MIB count selection, successful internal PHY access using port-to-phy mapping, LED array indexing within bounds, and no sparse/compiler warnings for field width mismatches.
