# sources/distributed-fs/ceph-client/drivers/misc/rp1/Makefile

Purpose: builds the RP1 PCI support object when `CONFIG_MISC_RP1` is selected.

Important build rule: `obj-$(CONFIG_MISC_RP1) += rp1_pci.o`.

Control flow/state: no runtime logic; kernel build-system mapping only.

Dependencies and integration points: consumed by `drivers/misc` build.

Risks and test signals: compile with `MISC_RP1=m` and `=y` to catch missing exports in PCI, MSI, IRQ domain, and OF platform APIs.
