# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-leds.c

## Purpose

This file implements optional LED class support for QCA8K switch port LEDs. It parses LED child nodes under DSA ports, maps each LED to the QCA8K LED control registers, registers `led_classdev` instances, supports direct brightness and hardware 4 Hz blink, and offloads Linux netdev LED trigger rules into switch LED rule bits.

## Important APIs, Types, and Functions

- `qca8k_phy_to_port()` maps internal PHY indices to DSA port numbers.
- `qca8k_get_enable_led_reg()` maps per-port/per-LED enable-pattern bits to the correct register and shift, accounting for special port 1/2/3 packing in `QCA8K_LED_CTRL3_REG`.
- `qca8k_get_control_led_reg()` maps rule-control fields for PHY0-3 and PHY4.
- `qca8k_parse_netdev()` converts Linux netdev trigger bits into QCA8K LED rule masks.
- `qca8k_led_brightness_set()` and `qca8k_led_brightness_get()` implement direct always-off/always-on control.
- `qca8k_cled_blink_set()` implements hardware blink only for 125 ms on/off, equivalent to 4 Hz.
- `qca8k_cled_hw_control_*()` implements LED trigger offload support, including status, supported-rules check, set/get, and associated netdevice lookup.
- `qca8k_parse_port_leds()` parses one port's `leds` node and registers LED class devices.
- `qca8k_setup_led_ctrl()` walks device-tree ports and initializes user-port LEDs.

## Control Flow

`qca8k_setup_led_ctrl()` looks for the top-level `ports` node. It skips CPU ports 0 and 6, reads each user port's `reg`, converts the DSA port number to an internal PHY LED index, and calls `qca8k_parse_port_leds()`. Per LED, the parser validates `reg` against the maximum of three LEDs per PHY, fills a `struct qca8k_led`, applies the default state (`on`, `keep`, or off), assigns LED class callbacks, builds a mandatory device name from the internal MDIO bus ID and port number, registers with `devm_led_classdev_register_ext()`, and frees the temporary name.

Brightness and blink callbacks update the pattern-enable bits. Hardware trigger offload first enables rule-controlled mode for that LED and then writes the trigger rule field. The get path verifies that the LED is in rule-controlled mode before translating hardware rule bits back into Linux trigger bits. The associated device callback maps the LED's PHY/port to the DSA user netdevice.

## State and Persistence

Per-LED runtime state is stored in `priv->ports_led[]`: port number, LED number, old rule placeholder, private pointer, and embedded `led_classdev`. Hardware LED mode/rule state is stored in QCA8K LED control registers and persists until reconfigured or reset. The code does not maintain a software shadow of rule fields beyond the LED classdev state.

## Dependencies and Integration Points

This file depends on `CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT`, LED class APIs, LED default-state parsing, netdev trigger rule bits, fwnode/device property APIs, regmap, DSA port-to-netdev lookup, and constants/types from `qca8k.h` and `qca8k_leds.h`. It is included in the `qca8k` composite object only when Kconfig enables LED support.

## Risks and Edge Cases

The LED register layout is irregular; port 0/4 and ports 1-3 use different masks and shifts. Errors from `qca8k_get_enable_led_reg()` are ignored by callers that already expect valid port numbers, so invalid state would lead to bad register use. Hardware blink supports only 4 Hz; other delays intentionally fall back to software by returning `-EINVAL`. `qca8k_parse_netdev()` treats unknown nonzero rules as unsupported. Registration warnings do not abort setup for individual LED failures. The code assumes `priv->internal_mdio_bus` has been initialized before LED setup because it uses its ID in LED names.

## Test Signals

Test signals include LED class devices appearing for user ports with valid `leds` child nodes, no LED devices for CPU ports, default-state `on/off/keep` reflected in hardware, 125/125 blink offloaded to hardware, other blink rates falling back, netdev trigger offload for tx/rx/link/duplex bits, `hw_control_get_device` returning the user netdevice, and correct behavior for invalid LED `reg` values.
