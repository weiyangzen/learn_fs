# sources/distributed-fs/ceph-client/drivers/net/ethernet/silan/Makefile

Purpose: maps the Silan SC92031 Kconfig symbol to its object file.

Important entry: `obj-$(CONFIG_SC92031) += sc92031.o`.

Integration and state: kbuild-only file with no runtime behavior.

Risks and tests: symbol/object mismatch would omit the driver. Build-test `CONFIG_SC92031=y` and `m`.
