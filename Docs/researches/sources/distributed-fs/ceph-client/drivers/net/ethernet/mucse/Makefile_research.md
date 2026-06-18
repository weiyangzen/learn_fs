# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/Makefile

Purpose: vendor-level kernel build glue for Mucse Ethernet drivers.

Important declarations: `obj-$(CONFIG_MGBE) += rnpgbe/` descends into the rnpgbe subdirectory when the driver is enabled.

Control flow: Make/Kbuild only. The parent networking Makefile includes this directory; Kbuild conditionally visits `rnpgbe/`.

State and persistence: no runtime state. Build artifacts depend on `CONFIG_MGBE`.

Dependencies and integration: pairs with `mucse/Kconfig` and `mucse/rnpgbe/Makefile`.

Risks: symbol mismatch with Kconfig would silently skip or always build the driver. Current mapping is direct and minimal.

Test signals: kernel build with `CONFIG_MGBE=y`, `m`, and unset; verify `rnpgbe_main.o`, `rnpgbe_chip.o`, `rnpgbe_mbx.o`, and `rnpgbe_mbx_fw.o` are included only when intended.
