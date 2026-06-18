<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Makefile -->
# sources/distributed-fs/ceph-client/net/802/Makefile

This Makefile maps 802-layer configuration symbols to kernel objects. It builds `psnap.o` for LLC and AppleTalk users, `fc.o` for Fibre Channel net devices, `fddi.o` for FDDI, `stp.o` for STP, `garp.o` for GARP, and `mrp.o` for MRP.

The only control flow is kbuild conditional object selection with `obj-$(CONFIG_...)`. There is no runtime state. A subtle integration point is that `psnap.o` can be requested by both `CONFIG_LLC` and `CONFIG_ATALK`; kbuild coalesces duplicate object names in the built-in/module context.

Risks are build coverage and dependency mismatch with Kconfig. Tests should include all relevant configuration combinations, especially GARP selecting STP and VLAN GVRP/MVRP pulling in GARP/MRP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Makefile -->
