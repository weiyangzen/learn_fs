# sources/distributed-fs/ceph-client/drivers/usb/misc/usb251xb.c

## Purpose
`usb251xb.c` configures Microchip USB2422/USB251xB/USB251xBi/USB2517 USB 2.0 hub controllers through SMBus/I2C or, in platform mode, by reset/default configuration. It parses devicetree properties into the hub's internal register image, controls reset and power, attaches the hub, and supports suspend/resume by disabling and re-enabling the regulator.

## Important APIs, Types, and Functions
`struct usb251xb` stores device/I2C/regulator/reset resources plus one field per hub configuration register. `struct usb251xb_data` describes per-compatible defaults: product ID, downstream port count, LED support, battery-charging support, and product string. Static data covers `usb2422`, `usb2512b/bi`, `usb2513b/bi`, `usb2514b/bi`, and `usb2517/i`.

Key functions are `usb251xb_get_ofdata`, which parses devicetree into register fields; `usb251xb_get_ports_field`, which converts port-list properties to bitmasks; `usb251xb_reset`, which asserts/deasserts reset while optionally locking the I2C segment; `usb251xb_connect`, which writes the register image in 16-byte SMBus blocks and issues attach; `usb251x_check_gpio_chip`, which rejects unsafe reset GPIO placement on the same I2C segment; and `usb251xb_probe`, which validates configuration, enables `vdd`, registers regulator cleanup, and connects the hub.

## Control Flow
Both I2C and platform probes allocate `struct usb251xb`, set `hub->dev`, and call the common probe. If OF match data is available, `usb251xb_get_ofdata` reads IDs, power mode, over-current settings, TT mode, EOP disable, port switching, power/current limits, language ID, boost values, UTF-16 string descriptors, non-removable/disabled/swapped ports, and skip-config. The common probe checks for an I2C/reset-GPIO deadlock hazard, enables the regulator, and calls `usb251xb_connect`.

In I2C mode, `connect` either writes a minimal attach command when `skip-config` is set, or builds a 256-byte register image and writes it in sixteen SMBus block transactions before attach. In platform-only mode, no register interface exists, so reset is toggled and the hub uses default configuration. Suspend disables `vdd`; resume enables it and reruns `connect`.

## State and Persistence
All configuration is held in memory until written to the hub. The hardware register image is re-applied on resume. The regulator is managed by devm cleanup through `devm_add_action_or_reset`. No filesystem state exists.

## Dependencies and Integration Points
The driver depends on devicetree matching/properties, I2C SMBus block writes, optional reset GPIO, regulator framework, UTF-8 to UTF-16 conversion, and platform-driver fallback. It integrates with board descriptions through compatibles and properties such as `self-powered`, `bus-powered`, `non-removable-ports`, `sp-disabled-ports`, `bp-disabled-ports`, `power-on-time-ms`, `manufacturer`, `product`, `serial`, and `swap-dx-lanes`.

## Risks and Edge Cases
The reset GPIO cannot safely be provided by a GPIO controller on the same I2C segment as the hub, because the driver locks the segment around reset timing; the explicit child-device check prevents that deadlock/config-latch hazard. In platform-only mode, OF configuration fields may be parsed but many cannot be programmed without I2C. String lengths use the original UTF-8 length while data is converted to UTF-16LE, so descriptor length assumptions should be checked against hardware expectations. The SMBus write payload includes a count byte plus 16 data bytes; controller support for that block size is required. Invalid port numbers only warn, leaving the rest of the bitmask active.

## Test Signals
Validation should include OF parsing for every compatible, reset GPIO timing and bus-lock behavior, regulator enable/disable and devm cleanup, `skip-config` attach-only mode, full 256-byte I2C programming, platform-mode default attach, suspend/resume reconfiguration, and failure injection for SMBus write errors at different blocks.
