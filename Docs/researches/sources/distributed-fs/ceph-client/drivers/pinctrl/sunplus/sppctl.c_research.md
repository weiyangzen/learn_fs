# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.c

## Purpose
This file implements the Sunplus SP7021 pin controller and GPIO driver. It bridges the Linux pinctrl, pinmux, pinconf, and gpiolib APIs to SP7021 MMIO registers, while `sppctl_sp7021.c` supplies the SoC-specific pin/function/group tables declared in `sppctl.h`.

The driver supports three logical pin modes: fully-pinmux pins routed through MOON2 function control fields, group-pinmux functions routed through MOON1 group fields, and GPIO/IOP pins controlled by FIRST and MASTER registers plus GPIOXT direction/value/inversion/open-drain registers.

## Important APIs, Types, And Functions
- `struct sppctl_gpio_chip`: private GPIO wrapper containing GPIOXT and FIRST base addresses, embedded `gpio_chip`, and a spinlock for OE/direction-related register access.
- MMIO helpers such as `sppctl_first_readl`, `sppctl_gpio_master_readl`, `sppctl_gpio_oe_readl`, `sppctl_gpio_out_writel`, `sppctl_gpio_in_readl`, and inversion/open-drain helpers centralize register block offsets.
- Offset helpers `sppctl_get_reg_and_bit_offset`, `sppctl_get_moon_reg_and_bit_offset`, and `sppctl_prep_moon_reg_and_offset` translate GPIO offsets into register offsets and mask-protected MOON/GPIOXT write values.
- `sppctl_func_set`: configures fully-pinmux routing in MOON2. It subtracts `MUXF_L2SW_CLK_OUT`, packs mask and control fields, handles odd/even function placement, and writes the computed control word.
- `sppctl_gmx_set`: configures group pinmux fields in MOON1 using mask-protected writes.
- GPIO callbacks: `sppctl_gpio_get_direction`, `sppctl_gpio_direction_input`, `sppctl_gpio_direction_output`, `sppctl_gpio_get`, `sppctl_gpio_set`, `sppctl_gpio_set_config`, and optional `sppctl_gpio_dbg_show`.
- Pinconf callbacks: `sppctl_pin_config_get` and `sppctl_pin_config_set` support open-drain, level, IOP pseudo-config, inversion, output-low/output-high, and output-open-drain flags.
- Pinmux callbacks: `sppctl_get_functions_count`, `sppctl_get_function_name`, `sppctl_get_function_groups`, `sppctl_set_mux`, and `sppctl_gpio_request_enable`.
- Pinctrl callbacks: `sppctl_get_groups_count`, `sppctl_get_group_name`, `sppctl_get_group_pins`, optional `sppctl_pin_dbg_show`, `sppctl_dt_node_to_map`, and `pinctrl_utils_free_map`.
- Probe helpers: `sppctl_gpio_new`, `sppctl_group_groups`, `sppctl_pinctrl_init`, `sppctl_resource_map`, and `sppctl_probe`.

## Control Flow
`builtin_platform_driver(sppctl_pinctrl_driver)` registers a platform driver named `sppctl_sp7021`. A devicetree node with `compatible = "sunplus,sp7021-pctl"` invokes `sppctl_probe`. Probe allocates `struct sppctl_pdata`, maps four named MMIO resources (`moon2`, `gpioxt`, `first`, `moon1`), registers a `gpio_chip`, initializes and registers the pinctrl device, enables pinctrl, then adds the GPIO range to the pinctrl device.

GPIO requests enter through pinctrl's `.gpio_request_enable`. The driver reads FIRST and MASTER bits; if the pin is not already digital GPIO, it writes FIRST=GPIO and MASTER=GPIO using `sppctl_first_master_set`. Direction changes write mask-protected OE fields; output direction optionally writes an initial output value. Reads use GPIOXT IN registers; writes use GPIOXT OUT mask-protected fields.

Pinmux requests enter `sppctl_set_mux`. For fully-pinmux functions, the group selector is treated as a GPIO pin offset, FIRST is switched to mux mode, and MOON2 function routing is updated. For group-pinmux functions, every pin in the selected group is switched to mux mode and the MOON1 group field is updated. `sppctl_group_groups` builds a flattened group namespace: all GPIO pin names first, then every group-pinmux group, with `g2fp_maps` preserving function/group table indices.

Devicetree mapping accepts two styles. `sunplus,pins` is an array of packed 32-bit values: pin number in bits 31-24, pin type in bits 23-16, function in bits 15-8, and flags in bits 7-0. GPIO and IOP entries become `PIN_MAP_TYPE_CONFIGS_PIN`; fully-pinmux entries become `PIN_MAP_TYPE_MUX_GROUP`. Standard `function` plus `groups` properties add additional mux maps. `sunplus,zerofunc` immediately clears selected fully-pinmux or group-pinmux routes to "No map" during mapping.

## State And Persistence
Persistent hardware state lives in the SP7021 MOON1, MOON2, FIRST, and GPIOXT registers. The driver writes mask fields together with control fields to avoid unintended bit changes. Software state is devm-managed and tied to the platform device: MMIO bases, GPIO chip, pinctrl descriptor/device, GPIO range, flattened group names, and `g2fp_maps`.

The spinlock protects direction/OE-sensitive sequences and debug reads that depend on direction. Value writes and pinmux writes are direct MMIO operations without a global pinmux lock in this file, relying on subsystem serialization and mask-protected registers. There is no explicit suspend/resume save/restore; pin state persistence depends on hardware retention or normal pinctrl state reapplication by consumers.

## Dependencies And Integration Points
- Depends on gpiolib, pinctrl core, pinmux, generic pinconf, OF helpers, platform MMIO resource mapping, bitfield helpers, managed allocation, and debugfs seq output.
- Includes `<dt-bindings/pinctrl/sppctl-sp7021.h>` for packed devicetree constants such as `SPPCTL_PCTL_G_GPIO`, `SPPCTL_PCTL_G_IOPP`, `SPPCTL_PCTL_L_OUT`, and `MUXF_L2SW_CLK_OUT`.
- Includes `../core.h` and `../pinctrl-utils.h` for pinctrl internals and map freeing utilities.
- Consumes SoC data arrays from `sppctl_sp7021.c`: `sppctl_list_funcs`, `sppctl_pmux_list_s`, `sppctl_gpio_list_s`, `sppctl_pins_all`, `sppctl_pins_gpio`, and their size symbols.
- Integrates with the devicetree binding `sunplus,sp7021-pinctrl.yaml`, especially named resources and packed `SPPCTL_IOPAD(...)` values.

## Risks
- `sppctl_get_function_groups` searches `g2fp_maps` for the first group matching a function selector and then returns `&pctl->unq_grps[i]` with `*num_groups = f->gnum`. If the function has no mapped groups or index accounting drifts, this can point past the intended group range.
- `sppctl_dt_node_to_map` validates pin numbers for `sunplus,pins`, but fully-pinmux entries index `sppctl_list_funcs[pin_func]` without an explicit `pin_func < sppctl_list_funcs_sz` check in that branch.
- `sunplus,zerofunc` performs hardware writes during DT map creation, so parsing a pin state has side effects beyond returning maps.
- FIRST register updates are read-modify-write without a dedicated lock in `sppctl_first_master_set`, so concurrent mux/GPIO transitions could race if subsystem-level serialization is insufficient.
- There is no explicit remove path or suspend/resume callback; this is acceptable for built-in platform use but should be revisited for real module unload or low-power retention requirements.
- The Kconfig help mentions module builds, while this file uses `builtin_platform_driver`; build and unload behavior should be tested if `CONFIG_PINCTRL_SPPCTL=m`.

## Test Signals
- Build/link tests must include both `sppctl.o` and `sppctl_sp7021.o` to satisfy all extern data symbols.
- Devicetree schema tests should cover `compatible`, named resources, `sunplus,pins`, `function`/`groups`, and `sunplus,zerofunc`.
- Runtime probe should map all four resources and register both gpiochip and pinctrl successfully.
- GPIO tests should verify request-enable changes FIRST/MASTER, input/output direction, initial output level, get/set value, open-drain, input/output inversion flags, and debugfs output.
- Pinmux tests should exercise fully-pinmux functions, group-pinmux functions, zerofunc clearing, invalid pin numbers, invalid function numbers, and mixed GPIO/IOP/pinmux states.
- Power-management tests should check whether register state survives suspend or is reapplied by consumer pinctrl states.
