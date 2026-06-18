<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/galaxy/Makefile

Purpose: Kbuild glue for the Aztech Sound Galaxy ISA drivers. It defines `snd-azt1605-y := azt1605.o` and `snd-azt2316-y := azt2316.o`, then wires those composite objects to `CONFIG_SND_AZT1605` and `CONFIG_SND_AZT2316`.

Important APIs/types/functions: no C APIs are defined here; the important integration points are the Kbuild object variables and `obj-$(CONFIG_...)` module selections.

Control flow: when the corresponding Kconfig symbol is enabled, Kbuild compiles either wrapper file. Each wrapper includes `galaxy.c`, so the shared driver body is built separately with chip-specific preprocessor constants.

State and persistence: no runtime state; build output names determine loadable module identity.

Dependencies and integration: depends on ALSA ISA build infrastructure and the wrapper/source include-template pattern in the same folder. Risks are mostly build-time: changing object names or config symbols would disconnect the drivers from Kconfig. Test signals are successful kernel build with both symbols enabled independently and checking that only the selected modules are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/Makefile -->
