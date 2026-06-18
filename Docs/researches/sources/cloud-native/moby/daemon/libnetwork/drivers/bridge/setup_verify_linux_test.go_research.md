# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux_test.go

Purpose: Tests bridge IPv4 verification behavior against a temporary Linux bridge.

Important APIs and functions: `setupVerifyTest` creates a `netlink.Bridge` named `default0` and returns a `bridgeInterface`. `TestSetupVerify` verifies success with the requested IPv4 address assigned. `TestSetupVerifyBad` expects failure for a different IPv4 address. `TestSetupVerifyMissing` expects failure when no IPv4 address exists.

Control flow: each test runs in a temporary OS network namespace, creates a bridge, optionally assigns an address, then calls `setupVerifyAndReconcileIPv4`.

State and persistence: manipulates only temporary namespace link/address state.

Dependencies and integration points: tests `setup_verify_linux.go` and netlink bridge address operations.

Risks: covers basic verification but not isolated gateway mode, mask mismatches, or `bridgeInterfaceExists` behavior.

Test signals: good regression coverage for the main error branches in IPv4 bridge verification.
