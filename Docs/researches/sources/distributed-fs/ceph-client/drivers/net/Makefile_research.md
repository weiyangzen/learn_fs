# sources/distributed-fs/ceph-client/drivers/net/Makefile

Purpose: top-level build manifest for network device drivers. It maps configuration symbols to object files or subdirectories.

Important build entries in scope: `obj-$(CONFIG_AMT) += amt.o` builds the AMT virtual tunnel driver; `obj-$(CONFIG_NETDEV_LEGACY_INIT) += Space.o` builds boot-time legacy probe support; `obj-$(CONFIG_ARCNET) += arcnet/` descends into the ARCNET Makefile. The file also unconditionally descends into some core PHY-related folders via `obj-y` and conditionally includes many network families.

Control flow and integration: no runtime control flow exists. Build integration is symbol-driven; Kconfig controls whether each object is built-in or modular. The ARCNET subdirectory has a second Makefile that maps packet format and chipset options. AMT builds as one object and exports the rtnetlink alias through module metadata.

State and persistence: state is generated build output and module metadata. Risks include mismatched Kconfig/Makefile names, missing subdirectory inclusion, and unintentionally building legacy `Space.o` outside ISA configs. Test signals are targeted `make drivers/net/amt.o`, `make drivers/net/Space.o`, `make drivers/net/arcnet/`, full `M=drivers/net` module builds, and checking generated modules for expected names.
