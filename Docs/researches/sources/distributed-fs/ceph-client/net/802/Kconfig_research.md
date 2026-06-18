<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Kconfig -->
# sources/distributed-fs/ceph-client/net/802/Kconfig

This Kconfig fragment declares build-time switches for IEEE 802 support helpers. It defines tristate symbols `STP`, `GARP`, and `MRP`.

`STP` selects `LLC`, because the spanning-tree SAP demux depends on LLC SAP registration and PDU parsing. `GARP` selects `STP`, since GARP traffic is received through the STP/bridge-group LLC SAP demultiplexer. `MRP` is a standalone tristate here; VLAN MVRP selects it from the 802.1Q Kconfig.

There is no runtime control flow or persistent state. The integration point is Kconfig dependency propagation into the Makefile and dependent subsystems such as VLAN GVRP/MVRP.

Risks are configuration omissions: enabling GARP must pull in STP/LLC, while MRP users must ensure packet receive infrastructure is compiled. Test signals are configuration matrix builds with `STP=m/y`, `GARP=m/y`, and `MRP=m/y`, plus dependent VLAN options selecting the expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Kconfig -->
