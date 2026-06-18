# sources/distributed-fs/ceph-client/drivers/firmware/xilinx/Kconfig

## Purpose
This Kconfig fragment defines the configuration menu for Xilinx Zynq MPSoC firmware support. It controls whether the core ZynqMP firmware interface and its optional debugfs API surface are built.

## Important symbols
`ZYNQMP_FIRMWARE` is a boolean enabled under `ARCH_ZYNQMP`, defaults to yes for that architecture, and selects `MFD_CORE`. Its help text describes the firmware interface as the common platform-management service channel used by other drivers. `ZYNQMP_FIRMWARE_DEBUG` is a boolean depending on both `ZYNQMP_FIRMWARE` and `DEBUG_FS`; it enables debug APIs.

## Control flow and integration
Kconfig has declarative control flow. The enclosing menu is visible only for `ARCH_ZYNQMP`. The core symbol gates compilation of `zynqmp.o`, `zynqmp-ufs.o`, and `zynqmp-crypto.o` through the sibling Makefile, while the debug symbol gates `zynqmp-debug.o` and the inline stubs in `zynqmp-debug.h`.

## State and persistence behavior
No runtime state is stored here. The persistent effect is the kernel build configuration, which decides whether firmware APIs and debugfs controls exist in the image.

## Dependencies and integration points
The fragment integrates with the architecture selection, debugfs availability, and the MFD subsystem. Downstream drivers that call exported ZynqMP firmware APIs implicitly depend on this configuration being present.

## Risks and test signals
Risks are mostly build-configuration risks: disabling the core symbol removes exported firmware services needed by platform drivers, while enabling debug APIs exposes a privileged debugfs command path. Test signals include expected objects in build logs for each config combination, `CONFIG_ZYNQMP_FIRMWARE=y` on ZynqMP defconfigs, and absence of debug object/stubs mismatch when `DEBUG_FS=n`.
