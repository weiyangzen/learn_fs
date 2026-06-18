<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-janz-ttl.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-janz-ttl.c

## Purpose
`gpio-janz-ttl.c` supports the Janz MODULbus VMOD-TTL module as a 20-line output-only GPIO controller.

## Important APIs, types, and functions
`struct ttl_module` stores the gpiochip, big-endian control register mapping, software shadows for ports A/B/C, and a spinlock. GPIO operations are `ttl_get_value()` and `ttl_set_value()`. Hardware setup is in `ttl_setup_device()` using `ttl_write_reg()`.

## Control flow
Probe requires `janz_platform_data`, maps module registers, resets the device, configures all ports open-drain outputs, drives zeroes, enables ports, initializes a dynamic gpiochip with get/set only, and registers it. Set operations update the relevant port shadow and write the full 16-bit port register.

## State and persistence behavior
The driver treats values as software shadow state; `get` returns the shadow instead of reading hardware. Shadows are initialized to zero during setup. Hardware state is reset on probe and not persisted across unload/reload.

## Dependencies and integration points
It is a platform child of the Janz MFD/MODULbus stack, depends on big-endian MMIO accessors, and uses platform data to confirm module context.

## Risks and edge cases
Inputs and direction changes are not supported even though the physical device is programmable. Returning cached values can hide hardware write failures or external changes. Probe resets all outputs low, which may be externally visible.

## Test signals
Test probe with and without platform data, initial hardware programming sequence, set/get shadow consistency, port A/B/C offset mapping, and behavior around module reset and all-zero output defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-janz-ttl.c -->
