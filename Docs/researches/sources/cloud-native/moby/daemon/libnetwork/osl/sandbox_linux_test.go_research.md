<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_linux_test.go

Purpose: Linux integration tests for the OSL network namespace sandbox implementation. The file exercises namespace creation, interface migration, address assignment, live restore, duplicate creation, garbage collection, and interface removal.

Important APIs and helpers: `generateRandomName`, `newKey`, and `newInfo` build temporary netns keys and veth/interface fixtures. `verifySandbox` opens the namespace path with `netns.GetFromPath` and checks expected destination interface names through `nlwrap.NewHandleAt`. `verifyCleanup` asserts namespace bind paths are removed. Tests call production APIs such as `NewSandbox`, `Namespace.AddInterface`, `SetGateway`, `SetGatewayIPv6`, `Destroy`, `Interface.Remove`, `setInterfaceIP`, and `setInterfaceIPv6`.

Control flow: each test creates isolated network context with `netnsutils.SetupTestOSContext`, creates veth pairs in the test namespace, then moves/configures interfaces into a sandbox. `TestLiveRestore` creates a second sandbox with `isRestore=true` and verifies existing addresses remain instead of being reconfigured destructively.

State and persistence: test state is kernel netns paths, veth links, IPv4/IPv6 addresses, routes, and gateway settings. Cleanup depends on `Destroy` removing namespace files and links.

Dependencies and integration points: uses netlink/netns, Docker `types.ParseCIDR`, `nlwrap`, and OSL `Namespace` internals. These are privileged Linux tests.

Risks and test signals: strong coverage for route-conflict errors, IPv6 DAD disabling via `IFA_F_NODAD`, namespace GC, duplicate sandbox keys, and interface add/remove. Risks are flakiness from kernel capabilities, permissions, and global temporary names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_linux_test.go -->
