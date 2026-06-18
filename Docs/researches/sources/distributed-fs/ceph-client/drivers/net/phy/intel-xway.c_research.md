<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/intel-xway.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/intel-xway.c

## Purpose
`intel-xway.c` is the PHYLIB driver for multiple Intel/Lantiq XWAY PHY11G and PHY22F revisions. It handles interrupt masking/status, RGMII internal delay programming and warnings, default LED setup, LED class hardware control, and an autonegotiation workaround for older gigabit revisions.

## Important APIs, Types, And Functions
The file is mostly stateless and registers many `phy_driver` entries in `xway_gphy[]`. Important helpers are `xway_gphy_config_init()`, `xway_gphy_rgmii_init()`, `xway_gphy_init_leds()`, `xway_gphy14_config_aneg()`, interrupt callbacks, and LED callbacks `xway_gphy_led_brightness_set()`, `xway_gphy_led_hw_is_supported()`, `xway_gphy_led_hw_control_get()`, `xway_gphy_led_hw_control_set()`, and `xway_gphy_led_polarity_set()`.

## Control Flow
`config_init()` masks all interrupts, applies a default LED configuration when no devicetree `leds` child exists, clears pending interrupts, and configures RGMII skew. For plain `rgmii`, the driver preserves strapped delays but warns if nonzero skew is detected because `rgmii` should mean no internal delay. For `rgmii-id`, `rgmii-rxid`, and `rgmii-txid`, it reads optional internal delay properties and defaults missing delays to 2 ns before writing MII control skew fields.

Revision 1.3/1.4 `config_aneg()` sets the multi-port-device bit in `MII_CTRL1000` as an erratum workaround, then calls generic autoneg. Interrupt enable acks pending status and writes a mask for link state change and auto-downspeed detection. LED control maps netdev link speed and activity triggers to XWAY MMD LED registers.

## State And Persistence
There is no private software state. Persistent hardware state includes interrupt masks, MIICTRL skew bits, LED direct/integrated control bits, MMD LED blink/constant/pulse registers, polarity inversion bits, and autoneg advertisement workaround bits.

## Dependencies And Integration Points
The driver depends on PHYLIB, OF child-node lookup for `leds`, `phy_get_internal_delay()`, MMD register access, and LED trigger APIs. It integrates with devicetree RGMII delay properties and optional PHY LED descriptions; absent LED nodes trigger legacy default LED programming.

## Risks
RGMII delay semantics are compatibility-sensitive: the driver deliberately warns but preserves strapped delays for `rgmii`. LED hardware trigger reconstruction in `get()` assumes caller-provided `rules` storage is cleared before ORing bits. Activity-only LED triggers are rejected because hardware requires link context. Older revision autoneg workaround applies only to driver entries that set `xway_gphy14_config_aneg()`.

## Test Signals
Test all registered PHY IDs, interrupt mask/status handling, RGMII mode warnings with strapped delays, DT RX/TX delay properties, default LED programming when no `leds` node exists, LED brightness/manual mode, hardware trigger combinations and unsupported activity-only triggers, polarity active-low/high, and rev 1.3/1.4 gigabit autoneg with MPD bit set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/intel-xway.c -->
