<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/fddi/Makefile

Purpose: Routes enabled FDDI driver Kconfig symbols to their Kbuild objects/subdirectories.

Important APIs/types/functions: `obj-$(CONFIG_DEFXX) += defxx.o`, `obj-$(CONFIG_DEFZA) += defza.o`, and `obj-$(CONFIG_SKFP) += skfp/` are the build rules.

Control flow: Kbuild compiles the Digital DEFXX object, DEC DEFZA object, and/or descends into the SysKonnect `skfp` directory according to the selected child Kconfig symbols.

State and persistence behavior: No runtime state. It is a build-routing file.

Dependencies and integration points: Depends on symbols from `drivers/net/fddi/Kconfig` and on the corresponding source files/subdirectory existing elsewhere in the tree.

Risks and test signals: Build tests should cover each driver as built-in and module where supported, plus all disabled. `CONFIG_SKFP=m` should descend into `skfp/` and produce the expected module rather than a flat object in this directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/fddi/Makefile -->
