# sources/distributed-fs/ceph-client/drivers/input/keyboard/Kconfig

Purpose: defines the kernel configuration menu for keyboard/input-key drivers under `drivers/input/keyboard`, including build choices, dependencies, selects, defaults, and help text.

Important APIs/types/functions: this is Kconfig metadata rather than C code. Key constructs are `menuconfig INPUT_KEYBOARD`, the `if INPUT_KEYBOARD` block, many `config KEYBOARD_*` tristate/bool entries, `depends on`, `select`, `default`, and module naming help text.

Control flow: enabling `INPUT_KEYBOARD` exposes the menu but does not itself build code. Individual options select drivers such as ADC ladder keys, ADP5520/5585/5588 keypads, Amiga/Atari/AT keyboards, GPIO/matrix keypads, I2C touch/key controllers, platform SoC keypads, ChromeOS EC keyboards, and others. Dependencies constrain options to required buses, MFD parents, architectures, OF, GPIO, I2C, MATRIXKMAP, or compile-test availability.

State and persistence: Kconfig selections persist in the kernel `.config` and control compilation as built-in, module, or disabled. This file itself has no runtime state.

Dependencies and integration: integrates with the top-level input Kconfig and the keyboard `Makefile`; each symbol is consumed by `obj-$(CONFIG_...)` rules. `select` entries pull common helpers such as `INPUT_MATRIXKMAP`, `SERIO`, `REGMAP_I2C`, `GPIOLIB`, `CRC8`, and `INPUT_VIVALDIFMAP`.

Risks: incorrect dependencies can allow compile failures or hide valid drivers. Overuse of `select` can force helper subsystems unexpectedly. Help text and module names must stay aligned with Makefile object names. Architecture defaults can change build coverage significantly.

Test signals: run Kconfig validation, randconfig/allmodconfig builds, targeted builds for early entries in this work item, and compare each `KEYBOARD_*` symbol against Makefile object mappings.
