# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-as3722.c

Purpose: Implements pinctrl, pinmux, pinconf, GPIO, and IRQ translation for the ams AS3722 PMIC's eight GPIO pins. It bridges Linux pinctrl/gpiolib operations to the parent AS3722 MFD register and IRQ helpers.

Important APIs and functions: Pinctrl exposes eight one-pin groups. Pinmux methods include function count/name/groups, `as3722_pinctrl_set()`, `as3722_pinctrl_gpio_request_enable()`, and `as3722_pinctrl_gpio_set_direction()`. Pinconf methods are `as3722_pinconf_get()` and `as3722_pinconf_set()`. GPIO methods are `as3722_gpio_get()`, `as3722_gpio_set()`, `as3722_gpio_direction_output()`, and `as3722_gpio_to_irq()`. Probe is `as3722_pinctrl_probe()`.

Control flow: Probe inherits the parent firmware node, obtains the parent `struct as3722`, registers pinctrl, registers a sleeping gpiochip, and adds a pin range. DT maps are handled by `pinconf_generic_dt_node_to_map_pin()`. Setting a mux writes the `IOSF` field in `AS3722_GPIOn_CONTROL_REG(group)`, records the active function, and forces output mode for output-like alternate functions. GPIO direction uses saved pinconf mode bits to compute an AS3722 GPIO mode. GPIO get chooses signal input or output register based on current hardware mode and applies inversion. GPIO set reads inversion state and updates `GPIO_SIGNAL_OUT_REG`.

State and persistence: `struct as3722_pctrl_info` stores the parent device pointer, pinctrl/gpio objects, current mux option per pin, and software pinconf mode properties in `gpio_control[]`. Hardware state persists in AS3722 control and signal registers. Pinconf set mostly updates the software shadow; the hardware mode is applied when GPIO direction is set.

Dependencies and integration points: Depends on the AS3722 MFD API (`as3722_read()`, `as3722_update_bits()`, `as3722_irq_get_virq()`), platform device children, generic pinconf DT utilities, gpiolib, and pinctrl. Compatible string is `ams,as3722-pinctrl`.

Risks: Pinconf state is partly deferred; changing bias/open-drain/high-impedance does not immediately rewrite hardware unless a direction operation occurs. `as3722_pinctrl_gpio_request_enable()` rejects GPIO use when `io_function` is nonzero, so stale function tracking would block GPIO. Unsupported high-impedance direction combinations return `-EINVAL`. All GPIO operations can sleep due to parent register access.

Test signals: Probe under the AS3722 MFD, DT function selection for all mux options, GPIO request rejection while alternate functions are active, pinconf get/set for bias/open-drain/high-impedance, input/output direction mode writes, inverted GPIO get/set, and `to_irq()` mapping are key tests.
