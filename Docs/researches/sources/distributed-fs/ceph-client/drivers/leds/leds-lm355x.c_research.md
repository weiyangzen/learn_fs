# sources/distributed-fs/ceph-client/drivers/leds/leds-lm355x.c

Purpose: platform-data I2C/regmap flash-lighting driver for TI LM3554 and LM3556, exposing flash, torch, and indicator LED class devices.

Important APIs/types/functions: chip-specific `lm355x_reg_data` tables encode register/mask/shift differences. `struct lm355x_chip_data` stores three classdevs, platform data, regmap, mutex, last fault flag, and register table. `lm355x_chip_init()` programs pin/pass modes. `lm355x_control()` reads fault flags, updates current registers, handles external pin modes, and writes operation mode. `pattern_store()` provides LM3556 indicator pattern sysfs.

Control flow: probe requires platform data and I2C, selects LM3554/LM3556 table from id, initializes regmap/mutex, configures pins, and registers flash, torch, then indicator. Brightness zero maps to shutdown. External torch/strobe/indicator pins cause brightness configuration without keeping I2C operation mode active.

State and persistence: last fault flag is cached for logging. Hardware registers hold current levels, pin config, operation mode, and LM3556 indicator pattern. Mutex serializes brightness calls.

Dependencies/integration: I2C regmap, platform data `leds-lm355x.h`, LED default triggers `"flash"`/`"torch"`, optional indicator sysfs group.

Risks: platform data is mandatory. There are hand-written unregister unwinds. `pattern_store()` lacks explicit mutex. External pin behavior changes the meaning of brightness requests.

Test signals: LM3554 and LM3556 register table coverage, fault flag logging, flash/torch/indicator max brightness, external pin modes, LM3556 pattern sysfs bounds, and remove shutdown write.
