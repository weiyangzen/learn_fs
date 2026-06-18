# sources/distributed-fs/ceph-client/drivers/mailbox/Makefile

## Purpose
Maps mailbox Kconfig symbols to object files for the Linux mailbox framework and controller drivers.

## Important APIs, Types, And Functions
This is a kbuild Makefile. `obj-$(CONFIG_MAILBOX) += mailbox.o` builds the generic framework. Each `CONFIG_*` appends the corresponding controller object, such as `arm_mhu.o arm_mhu_db.o` for `CONFIG_ARM_MHU`, `arm_mhuv2.o` for `CONFIG_ARM_MHU_V2`, `pcc.o` for `CONFIG_PCC`, and SoC-specific mailbox drivers for Qualcomm, MediaTek, Broadcom, Xilinx, RISC-V, and others.

## Control Flow
Kbuild expands `obj-y` and `obj-m` according to the final `.config`. Composite modules are not defined here; each listed source compiles as its own object/module except `CONFIG_ARM_MHU`, which includes both the regular and doorbell ARM MHU implementations under the same symbol.

## State, Dependencies, And Integration
There is no runtime state. The file depends on symbol definitions in `Kconfig` and source filenames in `drivers/mailbox`. It integrates with the kernel build system and module installation.

## Risks And Test Signals
Symbol/object drift is the main risk: missing objects silently omit drivers, and stale objects break builds. The shared `CONFIG_ARM_MHU` entry builds both `arm_mhu.o` and `arm_mhu_db.o`, so both must remain compatible with that Kconfig dependency set. Test signals include `make drivers/mailbox/`, allmodconfig, randconfig, and cross-checking new Kconfig entries against Makefile additions.
