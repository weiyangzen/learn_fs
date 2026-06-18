<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/zynqmp-pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/zynqmp-pm-domains.c

Purpose: Xilinx ZynqMP firmware-backed generic PM domain provider. It lazily maps firmware node IDs from DT phandles into a fixed pool of genpds and uses firmware requirements to power devices and retain wakeup capability.

Important APIs/types/functions: `struct zynqmp_pm_domain` wraps genpd, firmware `node_id`, and request state. `zynqmp_gpd_power_on/off()` call `zynqmp_pm_set_requirement()`. `zynqmp_gpd_attach_dev/detach_dev()` request/release firmware nodes on first/last device. `zynqmp_gpd_xlate()` maps phandle node IDs into the fixed `ZYNQMP_NUM_DOMAINS` pool. `min_capability` controls off-state requirement for older firmware parent compatibility.

Control flow: probe allocates 100 domain structs and domain pointers, initializes all as off with generic names `domainN`, and registers a provider on the parent firmware node. Xlate first searches existing node IDs, then stores new IDs in the first zero slot. Attach requests the firmware node only for the first attached device; detach releases after the last. Power-off inspects all devices and children for active wakeup paths and requests either minimum capability or wakeup capability.

State/persistence: firmware owns node state. Driver tracks whether a node was requested and which firmware node ID occupies each pool slot. `min_capability` is global module state set during probe based on firmware compatible.

Dependencies/integration: depends on `linux/firmware/xlnx-zynqmp.h`, genpd, OF platform, and firmware platform device named `zynqmp_power_controller`.

Risks: node ID 0 is used as the empty-slot sentinel, so real node ID 0 cannot be represented distinctly. `kasprintf()` names are not freed on remove. Provider is registered on the parent OF node, so parent/child device lifetime matters. Fixed 100-domain pool may be insufficient for future firmware IDs.

Test signals: multiple consumers with repeated and new node IDs, wakeup-enabled child hierarchy on suspend, attach/detach first/last transitions, non-`xlnx,zynqmp-firmware` parent capability behavior, and node ID boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/xilinx/zynqmp-pm-domains.c -->
