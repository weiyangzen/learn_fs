# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/pinctrl-starfive-jh7100.c

## Purpose
This is the complete pinctrl, pinmux, pinconf, GPIO, and GPIO-IRQ driver for the StarFive JH7100 SoC. It handles 64 GPIO-capable pads plus function-share pads, parses packed DT pinmux values, controls pad configuration, exposes a gpiochip, and services chained GPIO interrupts.

## Important APIs, types, and functions
`struct starfive_pinctrl` stores the gpiochip, pinctrl range, locks, MMIO bases, pinctrl device, and DT-registration mutex. `starfive_dt_node_to_map()` dynamically creates generic groups/functions from DT. `starfive_set_mux()` writes `GPON_DOUT_CFG`, `GPON_DOEN_CFG`, and optional GPI input selector registers from packed pinmux values. Pinconf is implemented by `starfive_pinconf_get()`, `starfive_pinconf_group_set()`, `starfive_padctl_get()`, and `starfive_padctl_rmw()`, with custom `starfive,strong-pull-up`. GPIO callbacks include direction, get/set, set_config, and pin-range registration. IRQ callbacks are `starfive_irq_ack/mask/mask_ack/unmask/set_type()` plus `starfive_gpio_irq_handler()`. `starfive_probe()` wires clocks, reset, pinctrl, optional signal group, gpiochip, and IRQ parent.

## Control flow
Probe maps `"gpio"` and `"padctl"` resources, enables the clock, deasserts reset, registers pinctrl, optionally writes `starfive,signal-group` to `IO_PADSHARE_SEL`, derives the GPIO-to-pin range from the selected signal group, then registers a gpiochip with one parent IRQ. DT pinctrl parsing requires each child to contain either `pinmux` or `pins` but not both. `pinmux` children create a mux map plus optional configs; `pins` children create config-only groups. Mux application writes per-GPIO output data/enable selectors and routes input selectors when `din != GPI_NONE`. GPIO direction operations program both mux registers and pad input/bias bits. IRQ set-type programs edge/level, both-edge, and polarity registers, and the chained handler dispatches set bits from the two masked-status registers.

## State and persistence behavior
Runtime state is devm-managed; hardware state lives in GPIO, padctl, and padshare registers. Raw spinlocks serialize low-level register RMW paths, while a mutex serializes dynamic group/function creation. The clock is disabled via devm action on detach. No explicit suspend/resume state save exists in this file, so persistence across low-power states depends on platform retention or pinctrl core state reapplication.

## Dependencies and integration points
The driver depends on StarFive JH7100 DT bindings for `PAD_GPIO()`, `PAD_FUNC_SHARE()`, `GPI_NONE`, `GPO_ENABLE`, and packed pinmux values. It integrates with generic pinctrl groups/functions, generic pinconf parsing, gpiolib, gpiolib IRQ helpers, clocks, resets, and DT resources named `gpio` and `padctl`.

## Risks
The selected `IO_PADSHARE_SEL` changes which 64 pads are GPIO-capable; value 0 disables GPIO registration entirely. Packed pinmux encoding must match DT bindings exactly, or mux writes will route wrong signals. `starfive_pinconf_group_set()` combines all configs into a single mask/value before applying to all pins; conflicting configs in one node are resolved by order in that local computation. Drive strength is clamped from 14 to 63 mA and quantized. The chained IRQ handler reads status into `unsigned long`, which is fine for 32-bit chunks but should stay aligned with register width assumptions.

## Test signals
Tests should cover probe with and without `starfive,signal-group`, invalid signal groups, dynamic DT groups with `pinmux` and `pins`, GPIO direction transitions, input selector routing, custom strong pull-up, bias/drive/slew configs, IRQ edge/level/both-edge handling, and debugfs pin output showing `dout/doen`. Hardware tests should validate GPIO registration disappears for signal group 0.
