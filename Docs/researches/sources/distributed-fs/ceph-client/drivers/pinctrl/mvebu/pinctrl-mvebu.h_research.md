# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-mvebu.h

Purpose: this header defines the table contract between MVEBU SoC-specific pinctrl drivers and the shared core. It describes MPP control callbacks, mux settings, pin modes, SoC-level pinctrl data, and the macros used to build compact pin/function tables.

Important APIs, types, and functions: `struct mvebu_mpp_ctrl_data` stores either an MMIO base or a regmap plus offset. `struct mvebu_mpp_ctrl` describes a controllable pin or pin group and its get/set/GPIO callbacks. `struct mvebu_mpp_ctrl_setting` stores the hardware mux value, function name, debug subname, variant mask, and computed GPIO capability flags. `struct mvebu_mpp_mode` binds a pin id to its settings. `struct mvebu_pinctrl_soc_info` is the SoC descriptor consumed by `mvebu_pinctrl_probe()`.

Control flow: SoC files use `MPP_FUNC_CTRL()` or `MPP_FUNC_GPIO_CTRL()` to declare controls, `MPP_FUNCTION()` or `MPP_VAR_FUNCTION()` to declare settings, `MPP_MODE()` to terminate each setting list, and `MPP_GPIO_RANGE()` to describe GPIO ranges. The core later fills control pin arrays, filters settings by `variant`, infers GPIO flags, and invokes exported get/set helpers.

State and persistence behavior: the header itself has no runtime state, but it establishes which fields are mutable. Notably, `flags` in settings and `pins` arrays in controls are written by the core, and some SoC drivers also mutate `variant` fields at probe. Register persistence is delegated to the implementation helpers.

Dependencies and integration points: this header depends on Linux pinctrl GPIO range types, regmap declarations from included users, and platform driver declarations. It is included by all MVEBU pinctrl table drivers and by `pinctrl-mvebu.c`.

Risks and test signals: `MPP_FUNC_CTRL()` allocates a compound-literal pin array inside static initializers; the core mutates it, so const-correctness is deliberately relaxed. `MPP_VAR_FUNCTION()` drops `subname` when debugfs is disabled, changing debug detail but not function names. The ABI relies on exact string names. Test by building with and without `CONFIG_DEBUG_FS`, compiling all SoC table drivers, and checking that every mode list is sentinel-terminated by `MPP_MODE()`.
