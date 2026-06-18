# sources/distributed-fs/ceph-client/drivers/firmware/Makefile

## Purpose
Builds the firmware driver directory according to Kconfig symbols. It maps top-level firmware options to object files and always descends into common firmware subdirectories whose internal Makefiles decide whether objects are built.

## APIs, Types, And Functions
The file is kbuild syntax. Important mappings include `CONFIG_ARM_SCPI_PROTOCOL` to `arm_scpi.o`, `CONFIG_DMI` to `dmi_scan.o`, `CONFIG_ISCSI_IBFT` to `iscsi_ibft.o`, `CONFIG_SYSFB` to `sysfb.o`, and unconditional `obj-y` descent into `arm_ffa/`, `arm_scmi/`, `efi/`, `imx/`, `psci/`, `qcom/`, `smccc/`, and other vendor directories.

## Control Flow
kbuild expands `obj-$(CONFIG_...)` entries based on `.config`. Directory entries route the build into nested firmware areas, while individual object entries compile directly into built-in or module targets.

## State, Persistence, And Dependencies
There is no runtime state. Build outputs are object files and modules determined by Kconfig. Dependencies are the symbols defined in `drivers/firmware/Kconfig` and subdirectory Kconfig files.

## Integration Points
This is the build-side counterpart of the firmware Kconfig menu. It controls whether firmware protocol providers and platform drivers become available to the rest of the kernel.

## Risks And Test Signals
Risks are missing object mappings, stale object names after source renames, and unconditional subdirectory traversal hiding broken nested dependencies. Build matrix coverage across built-in/module/disabled configurations is the main signal.
