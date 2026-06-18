# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/swarm_connect_test.go

Purpose: regression test for `ipfs swarm connect` when AutoConf is enabled and a daemon is already running. It guards a previous failure mode where AutoConf interfered with CLI fallback/API behavior and produced a generic connect error.

Important functions: `TestSwarmConnectWithAutoConf` and `testSwarmConnectWithAutoConfSetting`. The test runs two cases, AutoConf disabled and enabled, both expecting success.

Control flow initializes a test-profile node, sets `AutoConf.Enabled`, installs bootstrap peers from AutoConf fallback defaults, starts the daemon, waits three seconds, verifies `ipfs id`, then runs `ipfs swarm connect /dnsaddr/bootstrap.libp2p.io`. It checks exit code 0, stdout containing `success`, and `ipfs id` output with non-null `Addresses`. State is daemon process, bootstrap config, swarm connection attempts, and address output. Dependencies are public DNS/bootstrap reachability, harness, and Kubo daemon API routing. Risks include network flakiness, public bootstrap availability, and the fixed sleep. Test signal is a direct CLI regression check across the AutoConf toggle.
