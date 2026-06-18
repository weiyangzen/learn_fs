# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tb10x.c

## Purpose
`pinctrl-tb10x.c` is the Abilis TB10x SoC I/O mux driver. It exposes static pin descriptors and static mux groups, parses simple device-tree function declarations, and arbitrates shared two-bit port mux registers between peripheral functions and GPIO usage.

## Important APIs, Types, and Functions
The static data is extensive: `tb10x_pins[]` lists SoC pins, many `*_pins[]` arrays define groups, and `tb10x_pingroups[]` maps each group to a port, mode, and GPIO/non-GPIO flag. `struct tb10x_port` tracks the current mode and active function reference count per mux port. `struct tb10x_pinctrl` stores the MMIO base, pinctrl device, static group table, dynamic OF function table, mutex, port states, and a bitmap of pins currently requested as GPIOs.

Pinctrl callbacks expose static groups and parse DT nodes through `tb10x_dt_node_to_map()`, which requires `abilis,function`. Pinmux callbacks expose one group per parsed function, request GPIO mode through `tb10x_gpio_request_enable()`, release GPIOs through `tb10x_gpio_disable_free()`, and select muxes through `tb10x_pctl_set_mux()`.

## Control Flow
Probe maps the single mux register resource, initializes the mutex, points at the static group table, snapshots current hardware mode for all nine ports, scans child nodes with `abilis,function` into the flexible `pinfuncs[]` array, and registers pinctrl. When a consumer selects a state, `tb10x_dt_node_to_map()` creates one mux map from child node name to the requested function/group string. `tb10x_pctl_set_mux()` rejects incompatible port modes or pins already requested as GPIO, writes the port mode if no user is active, and increments the port count. GPIO request scans all groups to find whether the pin belongs to a GPIO-capable mux group, checks conflicts against active non-GPIO functions, records the pin in the GPIO bitmap, and writes the GPIO mode if needed.

## State and Persistence
Hardware mux state is a compact MMIO register with two bits per port. The driver snapshots initial modes but does not restore them on remove or suspend. Runtime arbitration state is in `ports[].mode`, `ports[].count`, and `gpios`; it is protected by `state->mutex`. Function reference counts are incremented in `set_mux()` but there is no corresponding function disable callback to decrement them, so selected peripheral functions effectively remain counted for the driver lifetime.

## Dependencies and Integration Points
This driver uses platform MMIO resources, OF child nodes with `abilis,function`, pinctrl utils for map allocation, and the pinmux GPIO request hooks used by external GPIO controllers/ranges. It does not register a gpiochip itself; it only arbitrates muxing for GPIO-capable pins. Integration depends on exact static group names matching the strings referenced in device tree.

## Risks
The missing function-free/decrement path means port `count` can only increase, which is acceptable for static board muxing but risky for dynamic state changes or unload/reload expectations. Because each parsed function exposes only one group string, DT mistakes are caught late by pinctrl matching. Conflict detection scans static groups and relies on group metadata being complete. GPIO-only groups with `port < 0` are always mapped and skip register writes. There is no pinconf, IRQ, or PM handling.

## Test Signals
Test DT parsing with valid and missing `abilis,function`, initial hardware mode snapshots, selecting multiple compatible functions on the same port, rejecting incompatible modes with `-EBUSY`, GPIO request conflicts against active functions, function conflicts against requested GPIOs, and static group/pin enumeration. A useful stress test is repeated state selection/freeing to document the monotonic `ports[].count` behavior.
