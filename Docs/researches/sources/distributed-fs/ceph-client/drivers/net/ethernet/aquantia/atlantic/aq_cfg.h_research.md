## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_cfg.h

Purpose: central compile-time defaults and constants for Atlantic driver sizing, features, timing, and metadata.

Important APIs/types: defines default/max vectors and traffic classes, TX/RX descriptor counts, interrupt moderation modes and max usec value, queue/ring frame limits, RX refill thresholds, XDP page order, LRO/RSS defaults, PCI function capacities, service timer intervals, restart thresholds, flow-control and WOL defaults, autoneg/speed/MTU defaults, lock retry count, and driver name/description/author strings.

Control flow: no functions. These constants parameterize allocation, feature defaults, ethtool validation, ring sizing, and module metadata.

State and persistence: constants only; runtime values are copied into `aq_nic_cfg_s` elsewhere.

Dependencies/integration: included by `aq_common.h`, then broadly across Atlantic. `AQ_CFG_DRV_NAME` is used by module init, logs, ethtool, and hwmon naming.

Risks: changing descriptor, queue, or frame limits affects memory use, XDP constraints, ethtool ring bounds, and hardware programming expectations. The MTU default includes Ethernet header semantics used elsewhere.

Test signals: compile, driver load with default config, ethtool ring/coalesce validation, RSS queue setup, XDP MTU boundary tests, and WOL default behavior.
