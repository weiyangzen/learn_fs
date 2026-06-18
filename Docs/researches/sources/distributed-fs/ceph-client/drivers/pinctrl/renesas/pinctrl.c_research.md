# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl.c

## Purpose

`pinctrl.c` is the SuperH/R-Mobile/R-Car Pin Function Controller pinctrl integration layer. It adapts the common `struct sh_pfc` core and per-SoC `struct sh_pfc_soc_info` data tables into Linux pinctrl, pinmux, and pinconf operations. It does not define a specific SoC's pins; instead it consumes the tables and helper callbacks declared in `sh_pfc.h` and implemented by the SH-PFC core/SoC files.

## Important APIs, Types, And Functions

`struct sh_pfc_pinctrl` owns the pinctrl descriptor, generated `pinctrl_pin_desc` array, per-pin software config state, and back-pointer to `struct sh_pfc`. `struct sh_pfc_pin_config` tracks whether a pin is currently GPIO-enabled and the last mux mark configured for function mode. These software flags allow the pinmux ops to reject function muxing while GPIO owns a pin and to restore function mux after GPIO free.

Pinctrl group/function ops are thin accessors over `pfc->info->groups` and `pfc->info->functions`. DT mapping is implemented by `sh_pfc_dt_node_to_map()` and `sh_pfc_dt_subnode_to_map()`, which parse `function`, `groups`, `pins`, and generic pinconf properties into pinctrl maps. Muxing is implemented by `sh_pfc_func_set_mux()`, which calls `sh_pfc_config_mux()` for every group mux mark under `pfc->lock`.

GPIO handoff is handled through pinmux callbacks: `sh_pfc_gpio_request_enable()`, `sh_pfc_gpio_disable_free()`, and optionally `sh_pfc_gpio_set_direction()` when `CONFIG_PINCTRL_SH_PFC_GPIO` is enabled. Pinconf support includes bias, drive strength, and power source through `sh_pfc_pinconf_get()`, `sh_pfc_pinconf_set()`, and `sh_pfc_pinconf_group_set()`. Helper functions `rcar_pinmux_get_bias()`, `rcar_pinmux_set_bias()`, `rmobile_pinmux_get_bias()`, and `rmobile_pinmux_set_bias()` implement common SoC bias register patterns.

## Control Flow

`sh_pfc_register_pinctrl()` is called by the SH-PFC core after `struct sh_pfc` and its `info` table are ready. It allocates the wrapper, maps SoC pins into pinctrl descriptors with `sh_pfc_map_pins()`, fills the pinctrl descriptor with ops and pin arrays, registers/enables pinctrl, and returns status to the core.

For mux state application, the pinctrl core selects a function/group. `sh_pfc_func_set_mux()` takes the global PFC spinlock, checks that no group pin is currently owned as GPIO, applies each mux mark through the core's `sh_pfc_config_mux()`, and records successful mux marks in `configs[]`. GPIO request either marks the pin as GPIO-owned or, when no separate GPIO chip exists and no function mux has been set, explicitly configures the pin's enum ID as GPIO. GPIO free clears ownership and reapplies the saved mux mark if one exists.

Pinconf validation is per-pin and table-driven by `SH_PFC_PIN_CFG_*` flags. Bias get/set delegates to SoC ops, drive-strength get/set searches `drive_regs`, and power-source get/set uses a SoC `pin_to_pocctrl()` callback to locate the POCCTRL bit and convert the table's allowed voltage range into low/high millivolt values.

## State And Persistence

The layer maintains per-pin software state for GPIO ownership and saved mux marks. Hardware state lives in SH-PFC registers accessed through `sh_pfc_read()`, `sh_pfc_write()`, and `sh_pfc_config_mux()`. All critical hardware and software state updates use `pfc->lock`. This file does not implement suspend/resume itself; persistence depends on the broader SH-PFC core and platform power behavior.

## Dependencies And Integration Points

The file depends on `drivers/pinctrl/renesas/core.h`, local `sh_pfc.h`, generic pinctrl/pinmux/pinconf APIs, OF mapping when `CONFIG_OF` is enabled, and optional SH-PFC GPIO integration. It is exported to other Renesas PFC code through `sh_pfc_register_pinctrl()` and bias helper declarations in `sh_pfc.h`.

## Risks

The mux/GPIO ownership model is intentionally conservative and can return `-EBUSY` if a consumer tries to mux a GPIO-owned pin. DT mapping permits function-only, config-only, and combined nodes; bad group/pin strings are not validated here and rely on pinctrl core lookup. Drive-strength conversion assumes a full-scale 24 mA model with 3 mA or 6 mA steps based on field width; inaccurate SoC tables or different electrical models would produce wrong values. Bias and power-source behavior depends heavily on optional SoC callbacks and table flags.

## Test Signals

Tests should apply OF states with function/groups, config-only pins, and combined mux/config nodes; request GPIOs before and after function muxing; verify `-EBUSY` behavior; round-trip bias, drive-strength, and power-source configs on SoCs that provide the relevant tables; and cover missing optional SoC callbacks returning `-ENOTSUPP`.
