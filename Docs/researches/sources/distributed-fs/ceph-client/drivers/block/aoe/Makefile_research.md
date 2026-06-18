# sources/distributed-fs/ceph-client/drivers/block/aoe/Makefile

Purpose: builds the ATA over Ethernet driver as a composite Kbuild object when `CONFIG_ATA_OVER_ETH` is enabled.

Important entries: `obj-$(CONFIG_ATA_OVER_ETH) += aoe.o` selects the composite object as built-in or module. `aoe-y := aoeblk.o aoechr.o aoecmd.o aoedev.o aoemain.o aoenet.o` defines the compilation units linked into that object.

Control flow: Kbuild links the listed objects in the composite `aoe.o`. Runtime module entry and exit come from `aoemain.o`; the rest provide block, character, command, device, and network subsystems.

State and persistence: no runtime state. Build outputs depend on `.config` and Kbuild's built-in/module selection.

Dependencies and integration points: consumes `CONFIG_ATA_OVER_ETH` from `drivers/block/Kconfig`, and all objects share declarations in `aoe.h`. Any new AoE source file must be added here to link into the module.

Risks: object omission causes unresolved symbols or missing functionality at runtime. Test signals are `CONFIG_ATA_OVER_ETH=y/m` builds and module symbol resolution.
