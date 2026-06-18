# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/leds.c

Purpose: registers per-port LED class devices for supported mv88e6xxx ports and maps Linux LED brightness, blink, and `netdev` hardware-control rules onto switch LED selector registers.

Important APIs/types/functions: `mv88e6xxx_port_setup_leds()` parses firmware LED child nodes and registers LED classdevs. Helpers read/write the indirect port LED control register, force brightness, configure hardware blink periods, select hardware netdev trigger modes from `mv88e6352_led_hwconfigs`, and report supported/current rules.

Control flow: setup skips unsupported ports and missing firmware nodes, validates LED `reg` numbers 0/1, applies default state, fills classdev callbacks, constructs a device name, and registers via `devm_led_classdev_register_ext()`. Runtime callbacks take the switch register lock, read LED selector state, update only the relevant LED selector bits, and write back with the pointer/update bits.

State and persistence: LED mode lives in port hardware registers. Runtime classdev state is embedded in each `struct mv88e6xxx_port`. Firmware `default-state` can initialize hardware state during setup.

Dependencies/integration: depends on Linux LED classdev/netdev trigger APIs, firmware node APIs, DSA user device lookup, port register definitions, and the mv88e6xxx register lock.

Risks: the hardware-config table is marked MV88E6352-specific, so other families may be misrepresented if reused. Hardware blink supports only discrete periods; unsupported timing falls back to software. Only ports 0 through 5 are accepted.

Test signals: device-tree LED nodes should create LED devices, brightness on/off should force selectors, supported netdev trigger rules should program hardware selectors, unsupported rule combinations should return `-EOPNOTSUPP`, and blink period choices should match hardware values.
