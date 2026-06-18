# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Makefile

Purpose: Maps IBM Ethernet Kconfig symbols to object files and subdirectories.

Important build entries: `obj-$(CONFIG_IBMVETH) += ibmveth.o`, `obj-$(CONFIG_IBMVNIC) += ibmvnic.o`, `obj-$(CONFIG_IBM_EMAC) += emac/`, and `obj-$(CONFIG_EHEA) += ehea/` are the only build rules. They delegate EMAC and eHEA compilation to their subdirectory Makefiles.

Control flow: During kbuild traversal, enabled tristate symbols append either built-in or module targets. If `CONFIG_EHEA=m`, the `ehea/` subdirectory produces the `ehea.ko` module through its own Makefile. If disabled, the directory is skipped.

State and persistence: No runtime state. The persistent effect is kernel build output composition based on `.config`.

Dependencies and integration: Coupled to `drivers/net/ethernet/ibm/Kconfig` symbol names and to existing subdirectories/files. It integrates IBM Ethernet drivers into the larger `drivers/net/ethernet/Makefile` traversal.

Risks: Misspelled symbols or directory names would silently drop drivers from builds. The file contains no ordering constraints beyond kbuild line order; inter-driver dependencies must be encoded in Kconfig.

Test signals: `make drivers/net/ethernet/ibm/` under configurations enabling each symbol; module and built-in builds; `make M=drivers/net/ethernet/ibm/ehea` for EHEA.
