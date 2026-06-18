<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/netinit_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/netinit_linux_test.go

Purpose: regression tests for bridge network initialization failure paths, ensuring daemon recovery and cleanup when bridge setup fails.

Important APIs/types/functions: `TestNetworkInitErrorDocker0`, `TestNetworkInitErrorUserDefined`, and `TestNetworkCreateErrorNoBridge` use `daemon.Daemon`, `DOCKER_TEST_BRIDGE_INIT_ERROR`, bridge driver option `BridgeName`, `network.CreateNoError/Create`, `nlwrap.LinkByName`, and `netlink.LinkNotFoundError`.

Control flow: the default-bridge test starts a daemon, injects an init error for `docker0`, expects restart failure, clears the injection, and starts successfully. The user-defined test creates a named bridge network, restarts with injected failure, removes the failed network, clears injection, restarts, and recreates it. The create-error test injects failure before daemon start, attempts network creation, checks the error, and verifies no bridge link remains.

State/persistence: exercises daemon restart state, persisted user-defined network metadata, bridge link creation/deletion, and test-only environment variable fault injection.

Dependencies/integration: Linux-only bridge driver, daemon test harness, netlink wrappers, and internal network helpers.

Risks: relies on a test-only environment variable recognized by the daemon; if fault-injection semantics change, tests can give false failures. Cleanup must handle daemon processes that may have exited during startup.

Test signals: passing tests show bridge init errors do not permanently wedge default or user-defined network restore, and failed creates do not leak bridge devices.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/netinit_linux_test.go -->
