# sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-tusb320.c

## Purpose
TI TUSB320/TUSB320L USB Type-C CC controller driver with extcon output and optional Type-C class/USB role-switch integration. It verifies the chip signature, reports USB device/host state and polarity, optionally registers a Type-C port, and supports changing advertised port type/current mode.

## Important APIs, Types, and Functions
`struct tusb320_priv` owns regmap, extcon, variant ops, current attached state, optional Type-C port/capability, port type, power opmode, connector fwnode, and role switch. `tusb320_check_signature()` validates the register signature. Variant ops provide `set_mode()` and optional revision read; TUSB320L disables CC termination while changing mode. `tusb320_extcon_irq_handler()` maps REG9 attached state to extcon USB/USB_HOST and polarity. `tusb320_typec_irq_handler()` reads REG8/REG9, updates Type-C orientation, roles, mode/accessory, role switch, and power opmode. `tusb320_state_update_handler()` reads REG9, filters interrupt status unless forced, runs handlers, and clears interrupt status by writing REG9.

## Control Flow
Probe allocates state, creates I2C regmap, checks signature, selects variant ops from OF match data, optionally reads revision, registers extcon and optional Type-C port from a `connector` child, forces initial state update, resets the chip, forces another state update, determines IRQ trigger type, and requests a threaded IRQ. Runtime IRQs call `tusb320_state_update_handler(false)`. Type-C port operations call `tusb320_port_type_set()`, which maps source/sink/DRP/default requests to hardware mode writes. Remove unregisters Type-C resources.

## State and Persistence
`priv->state` caches current attached state and prevents mode changes while attached. Hardware mode, advertised current, reset, interrupt status, and CC state live in registers. Optional Type-C and role-switch frameworks cache their own last reported roles. Extcon state persists until changed by later IRQ/forced update.

## Dependencies and Integration Points
Uses I2C regmap, extcon provider properties, Type-C class, USB role switch, OF match data for `ti,tusb320` and `ti,tusb320l`, IRQ trigger metadata, and Type-C connector firmware properties such as `typec-power-opmode`.

## Risks
`tusb320_typec_remove()` unconditionally calls `usb_role_switch_put()`, `typec_unregister_port()`, and `fwnode_handle_put()` even when no connector was present; safety depends on those helpers tolerating NULL. If `devm_request_threaded_irq()` fails after Type-C probe, resources are manually removed, but devm extcon/regmap remain. Reset after initial state can change state, hence the second forced update is required. Accessory role handling makes best-effort guesses for debug accessories. Mode changes return `-EBUSY` when attached, which callers must handle.

## Test Signals
Validate signature mismatch, TUSB320 versus TUSB320L mode-setting paths, revision read, initial forced updates before and after reset, REG9 interrupt filtering, CC1/CC2 polarity, DFP/UFP/accessory states, Type-C connector absent/present, advertised current from firmware, role-switch updates, and IRQ trigger type inheritance.
