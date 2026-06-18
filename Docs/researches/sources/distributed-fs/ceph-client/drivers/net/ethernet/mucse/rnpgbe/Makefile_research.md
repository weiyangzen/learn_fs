# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/Makefile

Purpose: Kbuild file for the Mucse rnpgbe driver module.

Important declarations: `obj-$(CONFIG_MGBE) += rnpgbe.o` builds a composite object. `rnpgbe-objs` links `rnpgbe_main.o`, `rnpgbe_chip.o`, `rnpgbe_mbx.o`, and `rnpgbe_mbx_fw.o`.

Control flow: build-time only; it defines link composition and module naming.

State and persistence: no runtime state. The linked module contains PCI netdev glue, board initialization, raw mailbox transport, and firmware command wrappers.

Dependencies and integration: invoked through the vendor Makefile when `CONFIG_MGBE` is enabled.

Risks: adding new source files without extending `rnpgbe-objs` will compile nothing into the module. Link ordering is simple and currently does not rely on initcall order.

Test signals: `make M=drivers/net/ethernet/mucse/rnpgbe` or full kernel build for both built-in and module configurations.
