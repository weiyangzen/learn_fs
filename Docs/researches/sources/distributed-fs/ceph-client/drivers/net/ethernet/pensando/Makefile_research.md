# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Makefile

Purpose: Connects the Pensando Ethernet vendor directory to the Ionic driver subdirectory.

Important APIs/types/functions: `obj-$(CONFIG_IONIC) += ionic/` causes Kbuild to descend into `pensando/ionic` when the driver is enabled.

Control flow: There is no runtime behavior; this is a build-routing file controlled entirely by `CONFIG_IONIC`.

State and dependencies: Depends on the Kconfig option from the sibling `Kconfig` and the `ionic/Makefile`.

Risks and test signals: Build tests should verify that `CONFIG_IONIC=m` produces the module from the subdirectory and that disabling `IONIC` skips it cleanly.
