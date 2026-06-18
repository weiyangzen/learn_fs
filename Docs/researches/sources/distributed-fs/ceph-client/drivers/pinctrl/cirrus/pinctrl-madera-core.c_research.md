# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera-core.c

Purpose: Shared pinctrl core for Cirrus Madera codecs, combining generated single-pin GPIO groups, chip-specific alternate groups, common mux functions, and generic pinconf.

Important APIs/types/functions: `madera_pins`, `madera_mux_funcs`, and chip tables from `pinctrl-madera.h` drive the pinctrl device. Core callbacks include group enumeration, debug display, `madera_mux_set_mux()`, GPIO request/direction/free hooks, and `madera_pin_conf_get/set/group_set()`. `madera_pin_probe()` selects the chip descriptor by MFD type.

Control flow: probe inherits the parent fwnode, selects a chip table for CS47L15/35/85/90/92 families, sizes the descriptor to the chip GPIO count, registers and initializes pinctrl, optionally registers pdata mappings, enables pinctrl, and stores driver data. Muxing writes function codes into `MADERA_GPIOx_CTRL_1`; alt functions use function value 0 across chip-specific pin groups, while other functions target generated one-pin groups.

State and persistence: mux and pinconf state live in Madera codec registers. Driver state is devm-managed. Pinconf writes are batched as masks for two adjacent registers per pin.

Dependencies/integration: Madera MFD core/register headers, regmap, pinctrl, generic pinconf, pdata mappings, and chip-specific table objects.

Risks: `madera_pin_desc` is a static descriptor whose `npins` is mutated per probe, which would be risky if multiple Madera instances with different GPIO counts probed concurrently. Drive strength accepts only 4 and 8 mA; unsupported values warn and encode as 4 mA rather than returning an error. Input enable get checks CTRL_1 direction mask while set writes CTRL_2, worth hardware-register verification.

Test signals: probe each supported Madera type, check pdata mapping application, inspect debugfs pin states, test every pinconf parameter, verify strict GPIO/function exclusivity, and validate unsupported drive-strength behavior.
