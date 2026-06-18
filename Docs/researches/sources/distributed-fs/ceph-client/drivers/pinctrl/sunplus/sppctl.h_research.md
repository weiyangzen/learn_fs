# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/sppctl.h

## Purpose
This header defines the shared register constants, helper macros, enums, data structures, and extern SoC table declarations used by the Sunplus SP7021 pinctrl driver. It is the contract between the generic implementation in `sppctl.c` and the SP7021 data file `sppctl_sp7021.c`.

## Important APIs, Types, And Data
- `SPPCTL_MODULE_NAME`: shared driver/gpiochip name `sppctl_sp7021`.
- GPIOXT/FIRST register offsets: `SPPCTL_GPIO_OFF_FIRST`, `SPPCTL_GPIO_OFF_MASTER`, `SPPCTL_GPIO_OFF_OE`, `SPPCTL_GPIO_OFF_OUT`, `SPPCTL_GPIO_OFF_IN`, `SPPCTL_GPIO_OFF_IINV`, `SPPCTL_GPIO_OFF_OINV`, and `SPPCTL_GPIO_OFF_OD`.
- Fully-pinmux field masks: `SPPCTL_FULLY_PINMUX_MASK_MASK`, `SPPCTL_FULLY_PINMUX_SEL_MASK`, and `SPPCTL_FULLY_PINMUX_UPPER_SHIFT`.
- MOON mask helpers: `SPPCTL_MOON_REG_MASK_SHIFT`, `SPPCTL_SET_MOON_REG_BIT(bit)`, and `SPPCTL_CLR_MOON_REG_BIT(bit)`.
- `SPPCTL_IOP_CONFIGS`: sentinel config value used by `sppctl_pin_config_set` to switch a pin to IOP mode.
- Table-construction macros `FNCE`, `FNCN`, and `EGRP`: concise initializers for functions with explicit groups, functions without groups, and group descriptors.
- `enum mux_first_reg`: requested FIRST register action (`mux_f_mux`, `mux_f_gpio`, `mux_f_keep`).
- `enum mux_master_reg`: requested MASTER register action (`mux_m_iop`, `mux_m_gpio`, `mux_m_keep`).
- `enum pinmux_type`: distinguishes fully-pinmux functions from group-pinmux functions.
- `struct grp2fp_map`: maps flattened group selectors back to function and group indices.
- `struct sppctl_pdata`: per-device driver state shared across pinctrl/gpio operations, including four MMIO bases, pinctrl descriptor/device, GPIO range, GPIO chip pointer, flattened group names, and selector maps.
- `struct sppctl_grp`: named group value and pin list.
- `struct sppctl_func`: function name, pinmux type, register offset, bit offset/length, group list, and group count.
- Extern declarations for SP7021 data arrays and sizes: `sppctl_list_funcs`, `sppctl_pmux_list_s`, `sppctl_gpio_list_s`, `sppctl_pins_all`, `sppctl_pins_gpio`, and their size symbols.

## Control Flow
The header has no executable control flow. Its definitions drive compile-time layout and runtime interpretation in `sppctl.c`. The macros create static function/group records in `sppctl_sp7021.c`; the enums select behavior in `sppctl_first_master_set` and `sppctl_set_mux`; the extern arrays are consumed during probe, group construction, pinctrl operations, and GPIO registration.

## State And Persistence
`struct sppctl_pdata` describes all software state kept for a probed SP7021 pinctrl device. Because allocation in the implementation is device-managed, the lifetime is tied to the platform device. Hardware state represented by offsets and masks persists in MMIO registers outside the header.

## Dependencies And Integration Points
- Depends on Linux bit, gpio, pinctrl, spinlock, kernel, and type headers.
- The register layout constants must match SP7021 hardware and the named MMIO resources mapped in `sppctl.c`.
- The table macros are used by `sppctl_sp7021.c`; field order must remain consistent with `struct sppctl_func` and `struct sppctl_grp`.
- Devicetree constants from `include/dt-bindings/pinctrl/sppctl*.h` must remain aligned with `sppctl_func` ordering and function IDs.

## Risks
- `SPPCTL_IOP_CONFIGS` is a magic config sentinel (`0xff`); collisions with future packed pinconf values or flag combinations would alter behavior.
- The extern arrays and size symbols rely on exact linkage with the data object. Missing Makefile entries cause link failures, while mismatched ordering can cause wrong function selection at runtime.
- Register masks encode hardware write-protection semantics; an incorrect mask shift or field width can write the wrong control bits.
- `struct sppctl_pdata` exposes implementation details across the driver and data code, so adding another SoC may require careful separation of SP7021-specific assumptions.

## Test Signals
- Compile tests catch struct/macro initializer mismatches between this header and `sppctl_sp7021.c`.
- Link tests catch missing extern data definitions.
- Runtime GPIO/pinmux tests validate that offsets, masks, and enum values produce expected FIRST, MASTER, MOON1, MOON2, and GPIOXT register changes.
- DT binding tests should confirm that function IDs and packed pin constants remain aligned with `sppctl_list_funcs` ordering.
