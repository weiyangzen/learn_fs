# sources/distributed-fs/ceph-client/tools/include/uapi/linux/netdev.h

Purpose: generated Generic Netlink UAPI for the `netdev` family, exposing modern network-device capability, page-pool, NAPI, queue, queue-stats, DMA-buf, lease, and XDP/AF_XDP metadata queries and operations.

Important APIs/types: constants define family name/version and multicast groups. Enums describe XDP action features, XDP Rx metadata capabilities, XSK Tx feature flags, queue type, qstats scope, and NAPI threaded mode. Attribute enums cover device capabilities, page pool identity/stats, NAPI settings, queue identity/binding/leases, queue stats counters, DMA-buf binding, and leases. Commands include device/page-pool get and notifications, page-pool stats, queue get/create, NAPI get/set, qstats get, and bind Rx/Tx.

Control flow, state, and persistence: userspace discovers the `netdev` Generic Netlink family, sends command messages with typed attributes, and receives replies or multicast notifications. Operations can read capabilities/counters or mutate NAPI/queue/binding state depending on command. State belongs to netdev queues, page pools, NAPI instances, and namespace-scoped devices.

Dependencies and integration points: generated from `Documentation/netlink/specs/netdev.yaml`; integrates Generic Netlink/YNL tooling, AF_XDP, io_uring networking providers, page-pool recycling, DMA-buf networking, and driver capability reporting.

Risks and test signals: risks include generated-header/spec drift, assuming optional attributes are always present, counter width/availability differences by driver, and admin-permission failures for mutating commands. Tests should validate YNL schema conformance, dump devices/page pools/NAPI/queues, compare qstats to driver counters, subscribe to multicast groups, and exercise bind/create/set commands on supported drivers.
