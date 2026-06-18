<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/nat_windows_test.go -->
# sources/cloud-native/moby/integration/network/nat/nat_windows_test.go

Purpose: verifies that Docker's Windows `nat` driver rejects disabling IPv4.

Important APIs/types/functions: `TestWindowsNoDisableIPv4` calls `network.Create` with `network.WithDriver("nat")` and `network.WithIPv4(false)`, then asserts the error contains `IPv4 cannot be disabled on Windows`.

Control flow: setup obtains context and API client, attempts to create an IPv6-only NAT network, and expects failure instead of cleanup.

State/persistence: no successful persistent network is created; the test validates rejection at creation time.

Dependencies/integration: Windows network package harness, internal network helper, Docker API client, and gotest comparison assertions.

Risks: exact error text is part of the test signal and may need updating if user-facing wording changes while preserving behavior.

Test signals: passing test confirms the Windows NAT driver enforces IPv4 availability and surfaces a clear error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/nat_windows_test.go -->
