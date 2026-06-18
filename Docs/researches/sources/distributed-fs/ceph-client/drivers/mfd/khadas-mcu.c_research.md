# sources/distributed-fs/ceph-client/drivers/mfd/khadas-mcu.c

Purpose: I2C MFD core for Khadas system control MCU. It creates a cached regmap with readable/writeable/volatile policy and registers user-memory and optional fan-control child devices.

Important APIs/types/functions: `khadas_mcu_probe()`, `khadas_mcu_reg_volatile()`, `khadas_mcu_reg_writeable()`, `khadas_mcu_regmap_config`, and MFD cells `khadas-mcu-user-mem` and `khadas-mcu-fan-ctrl`.

Control flow: probe allocates `struct khadas_mcu`, initializes an I2C regmap using the register policy callbacks and maple cache, registers the user-memory child, then registers the fan-control child only when the device-tree node has `#cooling-cells`.

State and persistence: per-device state stores device and regmap. Some MCU registers are marked volatile, while factory identity/version/MAC/USID fields are marked read-only. Persistent user data is represented by child drivers, not directly written here.

Dependencies and integration: depends on OF compatible `khadas,mcu`, I2C regmap, `linux/mfd/khadas-mcu.h` register definitions, and MFD children for user memory and fan control.

Risks: incorrect register policy can cache volatile command/status data or allow writes to identity fields. Optional fan child depends solely on DT cooling-cell property.

Test signals: DT binding, regmap read/write policy, cache behavior for volatile registers, user-memory child probing, fan child creation on cooling-capable boards, and I2C error propagation.
