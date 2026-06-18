# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Kconfig

Purpose: Provides Kconfig entries for the UCSI core and platform-specific UCSI interface drivers.

Important APIs/types/functions: `TYPEC_UCSI` enables the core `typec_ucsi` module and depends on little-endian CPU plus optional USB role switch support. Child options include `UCSI_CCG`, `UCSI_ACPI`, `UCSI_STM32G0`, `UCSI_PMIC_GLINK`, `CROS_EC_UCSI`, `UCSI_LENOVO_YOGA_C630`, and `UCSI_HUAWEI_GAOKUN`.

Control flow and state: no runtime flow. Build-time selection controls which transport modules and helper integrations are compiled. `TYPEC_UCSI` selects `USB_COMMON` when debugfs is enabled.

Persistence behavior: none directly; configuration persists through kernel build configuration.

Dependencies/integration points: ties the UCSI core to ACPI, I2C, ChromeOS EC, Qualcomm PMIC GLINK, Lenovo/Huawei EC drivers, DRM bridge selections, and module naming documented in help text.

Risks: incorrect dependencies can create link failures or unusable drivers. The core excludes big-endian CPUs, which matters because UCSI command/data structures are handled as little-endian memory layouts. Optional transport entries must match Makefile object rules.

Test signals: Kconfig lint/build matrix with options as built-in and modules; randconfig coverage for optional debugfs, power_supply, DP altmode, TBT altmode, and transport drivers; menuconfig visibility checks for dependency combinations.
