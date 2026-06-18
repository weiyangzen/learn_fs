# sources/distributed-fs/ceph-client/include/linux/pinctrl/pinmux.h

Purpose: declares the pin multiplexing operation contract implemented by pin controllers that can route pins or pin groups to hardware functions or GPIO mode.

Important APIs and types: `struct pinmux_ops` includes pin request/free callbacks, function enumeration (`get_functions_count()`, `get_function_name()`, `get_function_groups()`), optional `function_is_gpio()`, `set_mux()` for function/group selection, GPIO acceleration hooks (`gpio_request_enable()`, `gpio_disable_free()`, `gpio_set_direction()`), and the `strict` ownership flag.

Control flow: pinctrl core requests pins before selecting mux settings, queries available functions and groups, checks ownership conflicts, calls `set_mux()` for device functions, and uses GPIO hooks when gpiolib asks to use pins as GPIOs. With `strict`, the core prevents simultaneous GPIO and mux owners for the same pin.

State and persistence: no state is stored here. Ownership, selected functions, and GPIO modes are tracked by pinctrl core and hardware registers in the controller driver. Settings are replayed through pinctrl state selection and PM callbacks.

Dependencies and integration points: depends on `pinctrl_dev` and `pinctrl_gpio_range` forward declarations. It integrates pinctrl providers, gpiolib GPIO requests, Device Tree function/group maps, and controller-specific mux programming.

Risks and test signals: risks include drivers failing to reject unavailable pins, inaccurate GPIO-function detection, group/function mismatches, direction changes not updating mux state, and insufficient `strict` enforcement. Test mux selection, GPIO request/free, GPIO direction changes, conflicting GPIO/function requests, one-group-per-pin controllers, and debug/error paths for unavailable groups.
