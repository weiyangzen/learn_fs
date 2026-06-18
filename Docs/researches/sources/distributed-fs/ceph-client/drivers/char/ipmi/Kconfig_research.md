# sources/distributed-fs/ceph-client/drivers/char/ipmi/Kconfig

Purpose: Kconfig menu defining the IPMI message handler, system interfaces, user interfaces, BMC-side interfaces, and related helpers.

Important APIs, types, and functions: symbols include `IPMI_HANDLER`, `IPMI_DEVICE_INTERFACE`, `IPMI_SI`, `IPMI_SSIF`, `IPMI_IPMB`, `IPMI_DMI_DECODE`, `IPMI_PLAT_DATA`, watchdog/poweroff options, BMC KCS/BT/SSIF choices, and `IPMB_DEVICE_INTERFACE`.

Control flow: `menuconfig IPMI_HANDLER` gates host-side IPMI features. Several options select common helpers such as `IPMI_PLAT_DATA` or `IPMI_KCS_BMC`. BMC-side KCS/BT/SSIF and IPMB device-interface options live outside the host-handler `if` block where appropriate, allowing BMC roles without the full host handler.

State and persistence: no runtime state; configuration choices persist in kernel build configuration.

Dependencies and integration: ties IPMI drivers to architecture, I2C/I2C slave, DMI, MFD, REGMAP_MMIO, SERIO, KUnit, and platform-specific dependencies.

Risks and test signals: dependency mistakes can make objects build without required subsystems or hide usable BMC interfaces. Tests should include `allmodconfig`, `randconfig`, host-only, BMC-only, I2C-less, DMI, KUnit, and architecture-specific configurations.
