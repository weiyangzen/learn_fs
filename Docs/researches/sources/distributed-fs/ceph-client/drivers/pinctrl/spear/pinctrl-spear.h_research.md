## `sources/distributed-fs/ceph-client/drivers/pinctrl/spear/pinctrl-spear.h`

Purpose: shared data model and helper macros for SPEAr pinmux machine-data drivers plus declarations for the common SPEAr probe/helper functions.

Important APIs/types/functions: `struct spear_pmx_mode` describes global pinmux modes. `struct spear_muxreg` describes one masked register write. `struct spear_gpio_pingroup` models GPIO mux groups. Macros `DEFINE_MUXREG`, `DEFINE_2_MUXREG`, and `GPIO_PINGROUP` create common table fragments. `struct spear_modemux`, `struct spear_pingroup`, and `struct spear_function` describe mux possibilities. `struct spear_pinctrl_machdata` aggregates pins, functions, groups, GPIO pingroups, optional GPIO callback, and optional mode data. `struct spear_pmx` stores runtime device, pinctrl device, machine data, and regmap. Inline `pmx_readl()`/`pmx_writel()` wrap regmap access. Pin macros `SPEAR_PIN_0_TO_101` and `SPEAR_PIN_102_TO_245` define PLGPIO pin descriptors.

Control flow: no direct runtime flow except inline regmap wrappers. The structures in this header drive `pinctrl-spear.c` runtime behavior: group/function enumeration, mux application, mode filtering, and GPIO mux handling.

State and persistence: no mutable state is allocated here. It defines the shape of SoC static machine data and the runtime `spear_pmx` container. Placeholder register values may be patched by `pmx_init_addr()` before use.

Dependencies and integration: depends on Linux gpio, io, pinctrl, regmap, and types headers. It is consumed by common SPEAr code and SoC-specific table files. Risks include typo-prone table macros, comments with misspellings but clear meaning, no type-level validation that groups/functions reference each other consistently, and very large pin descriptor macros that can hide ordering mistakes. Test signals include compile coverage of all SoC table users, pin/group/function enumeration checks, regmap read/write tracing, and validation that GPIO pin numbering matches PLGPIO chip numbering.
