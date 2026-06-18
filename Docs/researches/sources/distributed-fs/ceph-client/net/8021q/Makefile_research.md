<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Makefile -->
# sources/distributed-fs/ceph-client/net/8021q/Makefile

This Makefile builds the VLAN layer. It always builds `vlan_core.o` when `CONFIG_VLAN_8021Q` is enabled in either built-in or module form through `$(subst m,y,...)`, and builds the `8021q.o` module from `vlan.o`, `vlan_dev.o`, and `vlan_netlink.o`. Optional objects are `vlan_gvrp.o`, `vlan_mvrp.o`, and `vlanproc.o`.

There is no runtime state. Integration points are kbuild object aggregation and conditional compilation of optional protocol and procfs support. The split between `vlan_core.o` and `8021q.o` matters because core offload receive/GRO support can be needed by other networking paths.

Risks are missing optional objects when Kconfig symbols are enabled or duplicate core linkage. Tests should compile config combinations for VLAN core, module, GVRP, MVRP, and PROC_FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Makefile -->
