<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvmem/Kconfig

## Purpose
Defines the Kconfig menu for the Linux NVMEM framework, optional sysfs interface, layout parsers, and many platform-specific NVMEM provider drivers.

## Important APIs, Types, And Functions
The top-level symbols are `NVMEM` and `NVMEM_SYSFS`, with `NVMEM` implying `NVMEM_LAYOUTS`. This file sources `drivers/nvmem/layouts/Kconfig` and defines provider symbols such as `NVMEM_AN8855_EFUSE`, `NVMEM_APPLE_EFUSES`, `NVMEM_APPLE_SPMI`, `NVMEM_BCM_OCOTP`, `NVMEM_BRCM_NVRAM`, i.MX variants, Ingenic, LAN9662, Layerscape, Qualcomm, Rockchip, STM32, U-Boot environment, and others.

## Control Flow
Kconfig evaluation exposes provider choices only when `NVMEM` is enabled. Each provider constrains itself with architecture, bus, firmware, OF, MFD, or `COMPILE_TEST` dependencies and selects helper libraries such as regmap, CRC, SCM, or generic network utilities when needed.

## State And Persistence
No runtime state. The file controls compile-time inclusion, module availability, and default selections such as Broadcom iProc OCOTP defaulting on its architecture and STM32 OP-TEE helper being enabled when its parent and OP-TEE are enabled.

## Dependencies And Integration Points
Integrates the NVMEM core with platform buses, SoC architecture symbols, MTD, OP-TEE, SPMI, regmap, CRC, and layout parsers. Module names documented in help text map to Makefile objects.

## Risks
Missing dependencies can produce build failures on allyesconfig or unusable drivers on real systems. Overly broad defaults can expose unsafe write-capable OTP drivers; overly narrow dependencies can hide valid compile-test coverage. Layout symbols must remain aligned with `layouts/Makefile`.

## Test Signals
Run Kconfig coverage for defconfig, allmodconfig, and COMPILE_TEST architectures. Check that each selected symbol has a matching object in `drivers/nvmem/Makefile`, expected helper selections, and coherent module names in help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Kconfig -->
