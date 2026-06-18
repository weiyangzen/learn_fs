## sources/distributed-fs/ipfs-kubo/test/sharness/t0185-autonat.sh

Purpose: smoke-tests daemon startup with AutoNAT service mode enabled and disabled.

Important APIs and helpers: uses `test_init_ipfs`, `ipfs config AutoNAT.ServiceMode`, and daemon launch/kill helpers.

Control flow and state: sets `AutoNAT.ServiceMode` to `enabled`, launches and kills the daemon, then sets it to `disabled` and repeats. Persistent state is the AutoNAT config key.

Dependencies and integration points: covers AutoNAT service configuration parsing and daemon subsystem startup/shutdown.

Risks and test signals: catches invalid config values, startup panics, or stale subsystem state between daemon runs. Passing requires clean daemon lifecycle in both service modes.
