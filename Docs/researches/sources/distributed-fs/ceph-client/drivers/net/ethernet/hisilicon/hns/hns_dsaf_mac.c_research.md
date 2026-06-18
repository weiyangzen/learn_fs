# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.c

## Purpose
`hns_dsaf_mac.c` is the shared MAC layer for HNS DSAF ports. It discovers per-port configuration from OF/ACPI, chooses GMAC or XGMAC backends, initializes/reset ports, manages PHY attachment, MAC table entries, broadcast/multicast/unicast programming, MTU, pause, link status, LEDs, and stats/register passthrough.

## Important APIs and Functions
Public functions include `hns_mac_init`, `hns_mac_uninit`, `hns_mac_start`, `hns_mac_stop`, `hns_mac_reset`, `hns_mac_adjust_link`, `hns_mac_get_link_status`, `hns_mac_change_vf_addr`, `hns_mac_add_uc_addr`, `hns_mac_rm_uc_addr`, `hns_mac_set_multi`, `hns_mac_clr_multicast`, `hns_mac_set_mtu`, pause/autoneg helpers, stats/string/register helpers, promisc programming, LED updates, and FIFO wait. Internal configuration is handled by `hns_mac_get_cfg`, `hns_mac_get_info`, `hns_mac_init_ex`, `hns_mac_register_phy`, and `hns_mac_get_inner_port_num`.

## Control Flow
`hns_mac_init` enumerates child port nodes or falls back to legacy all-port initialization, allocates `hns_mac_cb` objects, obtains each port's PHY mode/media/syscon/PHY data, resets LEDs, chooses the register base, creates a backend driver via `hns_gmac_config` or `hns_xgmac_config`, resets and adjusts the MAC, and enables broadcast table entries. Runtime start/stop increments/decrements virtual user counts, toggles MAC RX/TX, clears link state, and resets LEDs. MAC address changes update DSAF TCAM entries and the backend station address for VM 0.

## State and Persistence
Each `hns_mac_cb` stores persistent per-port runtime state: PHY device/interface, media type, speed/duplex/link, max frame size, pause timer, CPLD/serdes regmaps, multicast mask, TCAM address indexes per VM, LED packet counters, hardware stats, and the backend `mac_driver`. The DSAF TCAM software mirror in `hns_dsaf_main.c` is mutated through calls from this layer.

## Dependencies and Integration Points
This file integrates the DSAF device with GMAC/XGMAC backends, PHY/MDIO, ACPI and OF firmware properties, syscon/regmap, CPLD LED control, RCB MTU constraints, and DSAF TCAM operations. It is called by the AE adapter for all netdev-facing operations.

## Risks
Initialization can partially create `mac_cb` objects before later ports fail; devm allocation mitigates memory leaks, but hardware/backend cleanup depends on caller unwind. `hns_mac_stop` uses a virtual-device counter and can leave hardware enabled until all users stop; incorrect balancing would hold a port open. `hns_mac_get_inner_port_num` embeds DSAF mode assumptions and queue topology, so invalid mode or VF values affect TCAM routing. ACPI PHY registration intentionally ignores missing PHY except `-EPROBE_DEFER`, which can hide platform description gaps.

## Test Signals
Probe with child-node and legacy no-child configurations, OF and ACPI paths, SGMII and XGMII ports, MTU boundary tests against buffer size and max BD count, MAC address add/remove including invalid addresses, multicast cleanup per VF, pause/autoneg behavior on v1/v2 and debug/service ports, LED updates on fiber ports, and repeated start/stop reference balancing.
