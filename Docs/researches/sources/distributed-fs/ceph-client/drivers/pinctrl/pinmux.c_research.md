# sources/distributed-fs/ceph-client/drivers/pinctrl/pinmux.c

## Purpose
Provides the core pinmux implementation used by the pinctrl subsystem. It validates pinmux ops and maps, arbitrates ownership between mux users and GPIO users, enables/disables mux settings, exposes debugfs views, and implements generic pin function storage when `CONFIG_GENERIC_PINMUX_FUNCTIONS` is enabled.

## Important APIs, Types, And Functions
Important exported or internal APIs include `pinmux_check_ops()`, `pinmux_validate_map()`, `pinmux_can_be_used_for_gpio()`, `pinmux_request_gpio()`, `pinmux_free_gpio()`, `pinmux_gpio_direction()`, `pinmux_map_to_setting()`, `pinmux_enable_setting()`, `pinmux_disable_setting()`, `pinmux_init_device_debugfs()`, and generic function helpers such as `pinmux_generic_add_function()` and `pinmux_generic_get_function_groups()`.

## Control Flow
Map-to-setting resolves a function name to a selector, validates the requested group against that function's group list, and stores function/group selectors in the setting. Enabling a setting obtains group pins, requests each pin, records `desc->mux_setting`, and calls the driver's `set_mux()`. Error paths release already requested pins. Disabling a setting frees only pins whose current mux setting still matches the setting being disabled. GPIO request/free paths allocate an owner string, update `gpio_owner`, and call optional driver GPIO hooks.

## State And Persistence
State lives in each `struct pin_desc`: `mux_owner`, `gpio_owner`, `mux_usecount`, and `mux_setting`, protected by `desc->mux_lock`. Module references are held while pins are requested. Generic functions are stored in `pctldev->pin_function_tree` and counted in `pctldev->num_functions`.

## Dependencies And Integration Points
Integrated with pinctrl core internals in `core.h`, driver `pinmux_ops`, driver `pinctrl_ops`, gpiolib pin ranges, debugfs, radix trees, and module reference counting. Debugfs exposes `pinmux-functions`, `pinmux-pins`, and writable `pinmux-select`.

## Risks
Strict controllers rely on correct ownership checks to prevent unsafe GPIO/mux overlap. The debugfs `pinmux-select` path calls driver `set_mux()` directly and does not update normal pin ownership state. Generic function removal decrements `num_functions`, which can leave sparse selector indexes if removals are not last-in-order. Callers must not free pins more times than requested.

## Test Signals
Core test signals include map validation failures, concurrent mux/GPIO request arbitration on strict and non-strict controllers, error unwinding from `set_mux()`, debugfs output consistency, generic function add/remove lookup behavior, and lockdep coverage around `mux_lock`.
