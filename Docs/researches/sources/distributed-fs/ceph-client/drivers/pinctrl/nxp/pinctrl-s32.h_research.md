# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32.h

Purpose: Provides the shared internal interface and data structures for NXP S32 pinctrl drivers. It lets SoC-specific files describe pins and memory ranges while delegating parsing, muxing, pinconf, GPIO-mode handling, and PM save/restore to the S32 common core.

Important APIs and types: `struct s32_pin_group` pairs generic `struct pingroup` data with an array of SSS mux values. `struct s32_pin_range` defines inclusive pin id ranges per MMIO resource. `struct s32_pinctrl_soc_data` supplies the immutable SoC pin descriptors and memory-region ranges. `struct s32_pinctrl_soc_info` is the runtime parsed function/group state used by the common core. Macros `S32_PINCTRL_PIN()` and `S32_PIN_RANGE()` construct pin descriptors and ranges. Exported functions are `s32_pinctrl_probe()`, `s32_pinctrl_suspend()`, and `s32_pinctrl_resume()`.

Control flow: The header has no executable logic. SoC drivers provide `s32_pinctrl_soc_data` to `s32_pinctrl_probe()`, which then registers the pinctrl device and parses DT-defined functions/groups. PM callbacks in SoC drivers call the exported suspend/resume functions.

State and persistence: No state is stored by the header. It defines which SoC data is immutable and which runtime state is allocated and populated by the common core. The suspend/resume declarations expose the persistent pad save/restore contract under PM sleep.

Dependencies and integration points: Depends on pinctrl core types such as `struct pingroup`, `struct pinctrl_pin_desc`, and `struct pinfunction`, and forward-declares `struct platform_device`. It is included by both `pinctrl-s32cc.c` and `pinctrl-s32g2.c`.

Risks: This is an internal ABI between S32 common and SoC-specific files. Changing structure fields requires coordinated edits in the core parser, mux code, PM code, and every SoC data file. `S32_PIN_RANGE()` ranges must match platform resources exactly or common regmap offset calculations will target the wrong MMIO area.

Test signals: Compile coverage for common and S32G2 objects, successful probe using `s32_pinctrl_soc_data`, correct DT group parsing into `s32_pin_group`, and suspend/resume builds under `CONFIG_PM_SLEEP` validate the header.
