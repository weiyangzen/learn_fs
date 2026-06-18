# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Makefile

Purpose: object composition for the usNIC verbs module.

Important entries: adds the Cisco ENIC include path, builds `usnic_verbs.o` for `CONFIG_INFINIBAND_USNIC`, and links forwarding, transport, UIOM, interval tree, vNIC resource management, IB main, QP group, sysfs, verbs, and debugfs objects.

Control flow: Kconfig selects whether `usnic_verbs-y` is compiled as built-in or module objects. The object list defines the integration boundary among ENIC-backed forwarding, RDMA verbs, resource allocation, and observability.

State and persistence: no runtime state.

Dependencies and integration: depends on headers from `drivers/net/ethernet/cisco/enic`; pairs with `Kconfig` and the parent RDMA Makefile to include the driver.

Risks: omitting `usnic_uiom_interval_tree.o` or `usnic_vnic.o` would leave referenced helper APIs unresolved. Include-path coupling to ENIC internal headers is fragile across ENIC reorganizations.

Test signals: module and built-in builds, `modpost` symbol resolution, and compile coverage when `CONFIG_INFINIBAND_USNIC=m/y`.
