# sources/distributed-fs/ceph-client/drivers/mailbox/Kconfig

## Purpose
Defines the Linux mailbox subsystem configuration menu and individual mailbox controller/test-client options for many SoC families and firmware interfaces.

## Important APIs, Types, And Functions
This is declarative Kconfig. `menuconfig MAILBOX` enables the mailbox framework. Nested symbols include ARM MHU/MHUv2/MHUv3, platform MHU, PL320, PCC, OMAP, Rockchip, Qualcomm, MediaTek, Broadcom, STM32, Tegra, Xilinx, RISC-V SBI MPXY, and many others. Dependencies constrain build visibility by architecture, OF/ACPI, `HAS_IOMEM`, AMBA, SBI, or `COMPILE_TEST`; selected symbols can also select helper infrastructure such as `GENERIC_MSI_IRQ`.

## Control Flow
Kernel configuration tools evaluate dependencies and user choices. If `MAILBOX` is disabled, all nested mailbox controller options are hidden and their Makefile objects are not selected. If enabled, each chosen tristate/bool symbol drives compilation and module availability.

## State, Dependencies, And Integration
The file persists build-time configuration in `.config`, not runtime state. It integrates directly with `drivers/mailbox/Makefile` through matching `CONFIG_*` symbols and indirectly with device-tree or ACPI platform discovery in each driver.

## Risks And Test Signals
Incorrect dependencies can expose drivers on unsupported builds or hide valid compile-test coverage. Help text and module names can drift from Makefile object names. Test signals include `allyesconfig`, architecture-specific defconfigs, `COMPILE_TEST` builds, Kconfig dependency warnings, and checking that every Makefile object has a reachable config symbol.
