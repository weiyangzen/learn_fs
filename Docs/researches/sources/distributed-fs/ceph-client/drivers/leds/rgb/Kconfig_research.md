# sources/distributed-fs/ceph-client/drivers/leds/rgb/Kconfig

Purpose: Kconfig menu for RGB and multicolor LED drivers under `drivers/leds/rgb`, gated by `LEDS_CLASS_MULTICOLOR`.

Important APIs, types, and functions: this is build configuration, not C code. It defines `LEDS_GROUP_MULTICOLOR`, `LEDS_KTD202X`, `LEDS_LP5812`, `LEDS_NCP5623`, `LEDS_PWM_MULTICOLOR`, `LEDS_QCOM_LPG`, and `LEDS_MT6370_RGB`. Each option declares dependencies such as `OF`, `I2C`, `PWM`, `SPMI`, or `MFD_MT6370`, plus selected helpers such as `REGMAP_I2C` and `LINEAR_RANGES`.

Control flow: menu visibility depends on `LEDS_CLASS_MULTICOLOR`. When an option is `y` or `m`, the matching Makefile object is compiled. Help text describes hardware support and module names.

State and persistence: Kconfig choices persist in kernel `.config` and control which drivers are available. There is no runtime state.

Dependencies and integration points: ties driver source files to kernel configuration symbols and dependency resolution. Some symbols referenced here, such as Qualcomm LPG, are outside this work item but share the same directory.

Risks and test signals: validate dependency completeness with randconfig/allmodconfig, especially that multicolor class dependencies are sufficient for every object. Ensure module names in help text match Makefile outputs and that `select` entries cover required helper libraries.
