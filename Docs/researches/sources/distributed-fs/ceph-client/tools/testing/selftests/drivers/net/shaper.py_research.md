# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/shaper.py

Purpose: Tests the netdev shaper generic netlink API for queue, netdev, node, grouping, delegation, duplicate leaves, and queue-update behavior.

Important APIs/functions: Uses `NetshaperFamily` methods `get`, `cap_get`, `set`, `delete`, and `group`. Test functions include `get_shapers`, `get_caps`, `set_qshapers`, `del_qshapers`, `set_nshapers`, `del_nshapers`, `basic_groups`, `qgroups`, `delegation`, `queue_update`, and `dup_leaves`.

Control flow: Main creates a `NetDrvEnv` with four queues, initializes capability flags on `cfg`, then runs tests. Each test first checks capabilities and skips unsupported scopes/metrics. Queue/netdev shapers are created, updated, grouped, deleted, delegated between scopes, and validated through exact netlink object comparisons.

State and persistence: Mutates shaper hierarchy on the tested interface, including queue and netdev handles, node ids, weights, metrics, and channel count during `queue_update`. Tests explicitly delete created shapers; environment cleanup removes netdevsim when used.

Dependencies and integration: Requires kernel netdev shaper netlink API, netdevsim or a driver with shaper support, ethtool channel changes for queue-update, and lib.py netlink wrappers.

Risks: Exact object equality can break when kernel adds optional attributes. Queue-update relies on channel count semantics and `cfg.rx_type`. Capability skips must remain aligned with API names.

Test signals: PASS means capabilities are reported, supported shapers can be set/read/deleted, grouped leaves carry parent/weight attributes, queue delegation/nesting works, duplicate leaves return EINVAL, and shapers tied to removed queues are deleted.
