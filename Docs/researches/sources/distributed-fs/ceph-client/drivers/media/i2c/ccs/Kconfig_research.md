# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/Kconfig

Purpose: Kconfig entry enabling the generic MIPI CCS/SMIA/SMIA++ camera sensor driver.

Important APIs/types/functions: Defines `config VIDEO_CCS` as a tristate named "MIPI CCS/SMIA++/SMIA sensor support". It depends on `HAVE_CLK` and selects `V4L2_CCI_I2C` and `VIDEO_CCS_PLL`.

Control flow: Build configuration only. When enabled as built-in or module, it causes the CCS driver objects from the sibling Makefile to be built and ensures required CCI and PLL helper support are selected.

State/persistence: No runtime state. The selected symbol persists only in kernel build configuration.

Dependencies/integration: Integrates the CCS sensor driver with the media I2C Kconfig tree. The `VIDEO_CCS_PLL` selection connects this driver family to `ccs-pll.c`.

Risks: Selecting `VIDEO_CCS_PLL` makes the PLL helper available whenever the sensor driver is enabled, but hidden dependencies in the broader tree must still provide I2C/media infrastructure. The short help text does not mention device-tree/ACPI binding requirements.

Test signals: `make menuconfig` should show the option when `HAVE_CLK` is true. Kernel config builds should include `CONFIG_VIDEO_CCS` and automatically include `CONFIG_VIDEO_CCS_PLL` and `CONFIG_V4L2_CCI_I2C`.
