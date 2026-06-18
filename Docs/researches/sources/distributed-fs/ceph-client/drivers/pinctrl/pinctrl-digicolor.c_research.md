# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-digicolor.c

## Purpose
This built-in platform driver supports the Conexant Digicolor CX92755 general-purpose pin mapping block. It exposes 144 pins as one-pin pinctrl groups, supports muxing each pin between GPIO and three client functions, and registers a simple MMIO gpiochip.

## Important APIs, Types, and Functions
`struct dc_pinmap` stores MMIO base, device, pinctrl device and descriptor, generated pin names, gpiochip, and spinlock. Register macros derive client select, drive, output, and input offsets per 8-pin collection. Pinctrl callbacks expose one group per pin. Pinmux callbacks include `dc_get_functions_count`, `dc_get_fname`, `dc_get_groups`, `dc_set_mux`, and `dc_pmx_request_gpio`. GPIO callbacks include direction input/output, get, set, and `dc_gpiochip_add`. Probe is `dc_pinctrl_probe`.

## Control Flow and State
Probe maps the MMIO resource, allocates pin descriptors and names, generates names `GP_A0` through `GP_R7`, fills the pinctrl descriptor, registers pinctrl, then adds the gpiochip and pin range. Mux setup uses `dc_client_sel` to find a 2-bit field in a client-select register and writes the selected function. GPIO request checks that the mux field is zero before allowing GPIO. Direction and output operations update per-collection drive and output registers under a spinlock; input reads the input register directly.

## State and Persistence Behavior
Persistent state is in memory-mapped Digicolor registers. The spinlock protects drive/output RMW operations but not mux RMW operations, so concurrent mux changes could race. Pin names and descriptors are devm-managed for the lifetime of the platform device. No IRQ or pinconf state is implemented.

## Dependencies and Integration Points
The driver integrates with platform bus, OF compatible `cnxt,cx92755-pinctrl`, pinctrl, pinmux, pinctrl utils, and gpiolib. It is registered with `builtin_platform_driver`, so it is built-in rather than module-loaded.

## Risks
The TODOs explicitly call out missing GPIO interrupt support and pad configuration. `dc_set_mux` lacks locking around client-select RMW. `dc_pmx_request_gpio` only checks mux state and does not switch to GPIO itself. All functions list all groups, so invalid board-level combinations are not filtered by the driver.

## Test Signals
Runtime tests should verify 144 generated pin names, mux field programming for all four functions, GPIO request rejection when a pin is muxed to a client, direction/value behavior per collection, pin range registration, and absence of unexpected pinconf/IRQ behavior.
