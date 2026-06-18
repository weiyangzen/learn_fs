# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux.go

Purpose: Verifies an existing Linux bridge matches IPv4 configuration and checks whether an interface name resolves to a bridge.

Important APIs and functions: `setupVerifyAndReconcileIPv4` skips isolated IPv4 gateway mode, obtains `FAMILY_V4` addresses through `bridgeInterface.addresses`, selects the configured address with `selectIPv4Address`, fails if no IPv4 address exists, and fails if a configured IPv4 address does not match the bridge. `bridgeInterfaceExists` uses `ns.NlHandle().LinkByName` and accepts only links whose type is `bridge`.

Control flow: verification is read-only except for logging through callers. Missing links matching netlink's "Link not found" string are converted to `(false, nil)`; other lookup errors are wrapped.

State and persistence: no persistent state. Reads kernel netlink state and returns validation errors.

Dependencies and integration points: used during bridge setup to decide whether an existing bridge can be reused. Depends on `ns.NlHandle`, `netlink`, and bridge address selection helpers.

Risks: detecting missing links by error string is brittle compared with typed errors. IPv4 validation checks IP equality but not mask equality. Isolated mode bypasses verification.

Test signals: `setup_verify_linux_test.go` covers matching address, mismatched address, and missing address; link-type checks are not directly covered.
