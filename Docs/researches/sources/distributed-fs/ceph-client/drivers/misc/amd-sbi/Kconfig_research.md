# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Kconfig

Purpose: declares configuration for AMD side-band RMI support over I2C/I3C and optional hwmon exposure.

Important APIs and symbols: `AMD_SBRMI_I2C` is a tristate depending on `I3C_OR_I2C` and ARM/ARM64/COMPILE_TEST. It selects `REGMAP_I2C` and conditionally `REGMAP_I3C`. `AMD_SBRMI_HWMON` is a bool depending on `AMD_SBRMI_I2C` and `HWMON`, with a guard against built-in driver plus modular hwmon.

Control flow: enabling `AMD_SBRMI_I2C` builds the transport and core as `sbrmi-i2c`. Enabling `AMD_SBRMI_HWMON` links in `rmi-hwmon.o` and causes probe to create hwmon power sensors.

State and persistence: configuration state persists only in the kernel build. Runtime state is in the corresponding driver objects.

Dependencies and integration points: integrates with BMC-side AMD APML management over I2C/I3C and with the hwmon subsystem for socket power telemetry and limit control.

Risks: the symbol name references I2C although the driver also registers an I3C driver. Users may assume it runs on the managed host, but help text correctly states it is intended for the BMC.

Test signals: Kconfig dependency checks for I2C-only, I3C-only, and hwmon combinations; module name verification; allmodconfig builds; and menu visibility on supported architectures.
