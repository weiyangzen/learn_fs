# sources/distributed-fs/ceph-client/drivers/pinctrl/visconti/pinctrl-common.c

## Purpose

This file implements the shared Toshiba Visconti pinctrl, pinmux, and pinconf logic. SoC-specific files provide descriptor tables and optional unlock hooks; this common file maps MMIO registers, registers the Linux pinctrl device, and implements pin configuration, group lookup, function lookup, mux selection, and GPIO mux enablement.

## Important APIs, Types, And Functions

- `struct visconti_pinctrl` is private runtime state containing MMIO `base`, `dev`, `pctl`, `pctl_desc`, SoC `devdata`, and a spinlock protecting register read-modify-write sequences.
- `visconti_pin_config_set()` supports `PIN_CONFIG_BIAS_PULL_UP`, `PIN_CONFIG_BIAS_PULL_DOWN`, `PIN_CONFIG_BIAS_DISABLE`, and `PIN_CONFIG_DRIVE_STRENGTH`.
- `visconti_pin_config_group_set()` applies the same config list to every pin in a group.
- `visconti_get_groups_count()`, `visconti_get_group_name()`, and `visconti_get_group_pins()` implement `struct pinctrl_ops`.
- `visconti_get_functions_count()`, `visconti_get_function_name()`, `visconti_get_function_groups()`, `visconti_set_mux()`, and `visconti_gpio_request_enable()` implement `struct pinmux_ops`.
- `visconti_pinctrl_probe()` is the exported common probe entry used by SoC-specific platform drivers.

## Control Flow

`visconti_pinctrl_probe()` allocates private state, stores `devdata`, initializes the spinlock, maps the first MMIO resource, copies SoC pin descriptors into a devm-managed `struct pinctrl_pin_desc` array, fills `pctl_desc`, calls `devm_pinctrl_register_and_init()`, runs the optional SoC unlock callback, and finally calls `pinctrl_enable()`.

Pin configuration enters through generic pinconf callbacks. The driver locks, iterates configs, and updates per-pin registers from the SoC descriptor offsets and shifts. Pull-up falls through to pull-down handling after setting the selector bit; pull-up and pull-down both fall through to the enable/disable write. Drive strength accepts 2, 4, 8, 16, 24, and 32 mA and maps those to a 4-bit DSEL code with `DIV_ROUND_CLOSEST(arg, 2) - 1`.

Mux selection locks, reads the group mux register, clears `mux->mask`, ORs `mux->val`, and writes the result. GPIO request enable uses the per-pin `gpio_mux` entry and forces that pin’s mux field to the GPIO value.

## State And Persistence

The private state is devm-managed and lives as long as the platform device. Hardware mux, pull, and drive settings persist in MMIO registers until changed or reset. Register access is serialized by `spin_lock_irqsave()` around each read-modify-write sequence. There is no software persistence across reboot or driver unbind beyond what the pinctrl subsystem and device tree reapply.

## Dependencies And Integration Points

The driver depends on Linux MMIO, platform device, OF, and pinctrl/pinmux/pinconf APIs. It includes pinctrl core internals `../core.h`, generic pinconf helpers, and `pinctrl-utils.h`. SoC-specific data comes through `struct visconti_pinctrl_devdata` from `pinctrl-common.h`.

Device-tree integration uses `pinconf_generic_dt_node_to_map_group`, meaning states are group-oriented. `pinconf_generic_dump_config` provides debug output. `pinmux_ops.strict = true` prevents simultaneous GPIO and mux ownership conflicts.

## Risks And Edge Cases

- `visconti_pin_config_set()` indexes `priv->devdata->pins[_pin]` directly. It assumes pin numbers match dense descriptor indexes; sparse or reordered pin numbers would break.
- Unsupported drive strengths return `-EINVAL`; unsupported config parameters return `-EOPNOTSUPP` and abort the remaining config list.
- Pull configuration intentionally uses fallthrough; missing or misunderstood fallthrough would change behavior.
- `visconti_gpio_request_enable()` indexes `gpio_mux[pin]` directly, also assuming a dense GPIO/pin index space.
- Register offsets, masks, and shifts are trusted SoC data; the common code does not validate overlap or range.

## Test Signals

Unit-level signals are difficult because this is kernel MMIO code. Practical tests include successful probe, pinctrl debugfs showing expected groups/functions, device-tree states applying I2C/SPI/UART/PWM/PCMIF groups, GPIO request ownership respecting strict mode, and pinconf writes for bias disable, pull-up, pull-down, and each accepted drive strength. Negative tests should check invalid drive strengths and unsupported pinconf parameters.
