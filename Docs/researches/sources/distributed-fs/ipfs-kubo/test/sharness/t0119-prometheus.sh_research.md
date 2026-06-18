## sources/distributed-fs/ipfs-kubo/test/sharness/t0119-prometheus.sh

Purpose: verifies Prometheus metrics exposure and metric-set changes caused by ResourceMgr config and the `flatfs-measure` profile.

Important APIs and helpers: uses `ipfs config --json Swarm.ResourceMgr.Enabled`, `test_init_ipfs_with_profile`, daemon launch/kill helpers, `curl` against the metrics endpoint, and filtering of Prometheus output.

Control flow and state: enables ResourceMgr, starts the daemon, collects metrics, filters relevant series, and checks the expected resource-manager metrics are present and stable. It repeats initialization with the `flatfs-measure` profile and checks additional flatfs-related metrics without losing baseline metrics.

Dependencies and integration points: covers daemon metrics server, Prometheus exposition format, resource manager instrumentation, profile-driven repo initialization, and flatfs datastore measurement hooks.

Risks and test signals: catches missing metrics after config/profile changes, unstable metric names, and disabled instrumentation. Passing is determined by expected metric lines after filtering and no loss of initial metric set.
