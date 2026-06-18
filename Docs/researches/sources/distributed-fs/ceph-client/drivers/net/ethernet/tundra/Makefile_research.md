# sources/distributed-fs/ceph-client/drivers/net/ethernet/tundra/Makefile

Purpose: Connects the Tundra Ethernet Kconfig option to the kernel build system.

Important APIs and definitions: The sole build rule is `obj-$(CONFIG_TSI108_ETH) += tsi108_eth.o`, so `tsi108_eth.c` is compiled when `CONFIG_TSI108_ETH` is built in or modular.

Control flow and integration: There is no runtime flow. Kbuild expands the `obj-*` assignment based on the resolved Kconfig value and links `tsi108_eth.o` into the built-in object list or module target.

State and persistence: The Makefile owns no state. The build artifact selection is derived from `.config`.

Dependencies and integration points: Depends on `drivers/net/ethernet/tundra/Kconfig` defining `CONFIG_TSI108_ETH` and on `tsi108_eth.c` plus its local/header dependencies being present in the same directory.

Risks: Any rename of `tsi108_eth.c` or Kconfig symbol must be reflected here. No subdirectory recursion or multi-object module composition exists, so adding helper files would require updating this Makefile.

Test signals: Compile with `CONFIG_TSI108_ETH=y`, `m`, and unset; verify built-in object or module generation; run `make M=drivers/net/ethernet/tundra` in module-capable configurations.
