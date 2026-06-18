# sources/distributed-fs/ceph-client/drivers/dca/Makefile

Purpose: kbuild recipe for the DCA service module.

Important APIs/types/functions: `obj-$(CONFIG_DCA) += dca.o` and `dca-objs := dca-core.o dca-sysfs.o`.

Control flow and state: when DCA is enabled, core provider/requester logic and sysfs class support are linked into one module/object.

Dependencies and integration: ties the Kconfig symbol to the two implementation files.

Risks and test signals: missing either object breaks exported APIs or sysfs provider/requester representation. Test built-in and module builds and exported symbol resolution for DCA providers/clients.
