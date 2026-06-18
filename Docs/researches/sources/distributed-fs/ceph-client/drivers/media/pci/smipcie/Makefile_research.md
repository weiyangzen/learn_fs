<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/Makefile

Purpose: kbuild rules for the SMI PCIe driver.

Important APIs, types, and functions: builds `smipcie.o` from `smipcie-main.o` and `smipcie-ir.o` when `CONFIG_DVB_SMIPCIE` is enabled. Adds include paths for media tuner and DVB frontend headers.

Control flow: kbuild compiles the two object files into one module/built-in object.

State and persistence: no runtime state. Build output follows kernel build configuration.

Dependencies and integration points: `drivers/media/tuners` and `drivers/media/dvb-frontends` include directories for frontend/tuner configs used in source.

Risks: include path assumptions couple this driver to in-tree frontend/tuner headers. New source files must be added to `smipcie-objs` or they will not link.

Test signals: `make M=drivers/media/pci/smipcie`, all referenced frontend headers resolvable, and resulting module contains main and IR symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/smipcie/Makefile -->
