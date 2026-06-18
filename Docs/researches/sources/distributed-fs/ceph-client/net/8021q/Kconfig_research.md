<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Kconfig -->
# sources/distributed-fs/ceph-client/net/8021q/Kconfig

This Kconfig fragment controls 802.1Q/802.1ad VLAN support. `VLAN_8021Q` is a tristate module/built-in option for VLAN interfaces. `VLAN_8021Q_GVRP` enables GARP VLAN Registration Protocol support and selects `GARP`; `VLAN_8021Q_MVRP` enables Multiple VLAN Registration Protocol support and selects `MRP`.

There is no runtime logic. The important integration behavior is dependency propagation from optional VLAN features to the generic registration-protocol modules in `net/802`.

Risks are build-time only: GVRP and MVRP code paths must be compiled consistently with the helper modules they call, and users must have the `ip` tooling or netlink/ioctl control path to create VLAN devices. Tests should include `VLAN_8021Q` built-in and modular builds, with and without GVRP/MVRP, and verify symbol availability for selected helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Kconfig -->
