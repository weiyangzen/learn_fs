# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/wcd939x-usbss.c

## Purpose

`wcd939x-usbss.c` is the Qualcomm WCD939x USBSS Type-C mux/switch driver. It programs an I2C regmap in the audio codec sideband switch block so SBU/USB/DP/audio accessory routes match Type-C orientation and mux mode, then forwards the same switch and mux events to the downstream codec mux objects.

## Important APIs, Types, and Functions

`struct wcd939x_usbss` stores the I2C client, reset GPIO, optional `vdd` regulator, typec switch/mux registrations, codec mux handles, current orientation, mode, SVID, and a mutex for serializing updates. `wcd939x_usbss_set()` is the central hardware programming routine for safe, USB, DisplayPort, mixed DP+USB, and audio accessory states. `wcd939x_usbss_switch_set()` updates orientation and then calls `typec_switch_set()` on the codec switch. `wcd939x_usbss_mux_set()` updates mode/SVID and then calls `typec_mux_set()` on the codec mux. Probe initializes regmap paging, power/reset sequencing, fixed analog tuning bits, safe-mode routing, and the Type-C switch/mux devices.

## Control Flow

Probe allocates state, gets regmap/reset/regulator resources, acquires peer codec mux and switch by fwnode, powers and resets the chip, applies default manual/boost/RCO/device-enable programming, calls `wcd939x_usbss_set()` in safe mode, and registers Type-C switch then mux. Runtime changes enter through Type-C switch or mux callbacks, take the mutex, update cached orientation/mode/SVID, reprogram the local USBSS routes, release the mutex, and forward the event to the codec-facing object. Remove unregisters mux/switch, disables the regulator, and drops codec references.

## State and Persistence Behavior

The driver persists only runtime cached orientation, mux mode, and SVID plus device handles. Hardware state is register-resident and reset/power-cycle volatile. The mutex protects against concurrent switch and mux callbacks producing interleaved route programming.

## Dependencies and Integration Points

It depends on I2C regmap with range paging, regulators, optional reset GPIO, `linux/usb/typec_mux.h`, DisplayPort altmode constants, and fwnode-discovered codec Type-C mux/switch providers. It integrates in the Type-C mux graph as both a local hardware controller and a forwarding shim to the codec path.

## Risks and Test Signals

Risks include optional regulator handling that treats every `devm_regulator_get_optional()` error as fatal, long manual register sequences that can leave partially switched routes on I/O failure, ignoring return values while writing audio linearizer coefficients, and mode/SVID combinations returning `-EOPNOTSUPP`. Test signals include probe power/reset timing, safe-mode setup, normal/reverse USB routing, DP C/E and D/F routing, audio accessory orientation swaps, forwarded codec events, and remove/unwind reference cleanup.
