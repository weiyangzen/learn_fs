# Research Report: subset-b-000183

Grouped research for Moby libnetwork bridge setup helpers, host/null drivers, ipvlan/macvlan drivers, overlay driver support, remote plugin driver API, and Windows overlay driver files. Each section preserves the original source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux_test.go

Purpose: Linux bridge IPv4 setup tests exercise the bridge device creation helper, IPv4 address programming, and default gateway storage behavior used by the bridge driver setup pipeline.

Important APIs and functions: `setupTestInterface` creates a `networkConfiguration` with `DefaultBridgeName`, builds a `bridgeInterface` around an `nlwrap.Handle`, and calls `setupDevice`. `TestSetupBridgeIPv4Fixed` validates `setupBridgeIPv4` by adding `192.168.1.1/24` and checking `AddrList` for `FAMILY_V4`. `TestSetupGatewayIPv4` validates `setupGatewayIPv4` accepts a gateway inside the bridge network and records it in `br.gatewayIPv4`.

Control flow: each test enters an isolated OS network namespace via `netnsutils.SetupTestOSContext`, opens a netlink handle, creates or prepares the bridge interface, calls the setup function under test, then inspects netlink state or in-memory gateway fields.

State and persistence: no datastore state is touched. The tests mutate only the temporary network namespace and `bridgeInterface` fields.

Dependencies and integration points: depends on `nlwrap`, `netlink`, and the bridge setup helpers defined in sibling files. It verifies integration between bridge setup code and Linux netlink address state.

Risks: tests require netlink namespace support and sufficient privileges. They cover the positive path but not invalid IPv4 gateway rejection or address replacement behavior.

Test signals: strong signal for bridge IPv4 address programming and gateway field assignment in an isolated namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv4_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux.go

Purpose: Implements Linux bridge IPv6 setup, including toggling `/proc/sys/net/ipv6/conf/<bridge>/disable_ipv6`, programming bridge IPv6 addresses, and validating the configured IPv6 default gateway.

Important APIs and functions: `linkLocalPrefix` records `fe80::/64`. `setupBridgeIPv6` reads the bridge `disable_ipv6` procfs file, disables IPv6 for isolated gateway mode, enables it otherwise, then delegates address reconciliation to `bridgeInterface.programIPv6Addresses`. `setupGatewayIPv6` validates that `DefaultGatewayIPv6` is contained in `AddressIPv6` and stores it in `bridgeInterface.gatewayIPv6`.

Control flow: isolated IPv6 mode returns early after disabling IPv6 and copying `AddressIPv6` into `i.bridgeIPv6`. Non-isolated mode ensures procfs contains `0\n`, then calls into the interface address programming routine.

State and persistence: mutates kernel procfs and netlink address state, plus in-memory `bridgeInterface` fields. There is no datastore persistence.

Dependencies and integration points: used as a bridge setup step by the Linux bridge driver. It depends on `networkConfiguration` gateway mode helpers and `bridgeInterface.programIPv6Addresses` from the bridge interface implementation.

Risks: `ipv6BridgeData[0]` assumes procfs returned at least one byte. Procfs writes require privilege and can fail on kernels or namespaces without IPv6 sysctls. Isolated mode deliberately suppresses kernel-assigned link-local addresses, so incorrect gateway mode selection can affect connectivity.

Test signals: covered by `setup_ipv6_linux_test.go` for enabling IPv6, address assignment, and gateway storage; isolated mode is not directly covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux_test.go

Purpose: Tests Linux bridge IPv6 setup by verifying procfs enablement, netlink address assignment, and gateway configuration.

Important APIs and functions: `TestSetupIPv6` creates a bridge through `setupTestInterface`, sets `AddressIPv6`, calls `setupBridgeIPv6`, reads `/proc/sys/net/ipv6/conf/<bridge>/disable_ipv6`, and checks the bridge has the requested IPv6 address. `TestSetupGatewayIPv6` verifies `setupGatewayIPv6` stores an in-subnet gateway in `br.gatewayIPv6`.

Control flow: tests run in a temporary network namespace, use `nlwrap.NewHandle`, call the implementation, then inspect procfs and netlink `FAMILY_V6` addresses.

State and persistence: only temporary namespace kernel state and in-memory `bridgeInterface` fields are mutated.

Dependencies and integration points: exercises `setup_ipv6_linux.go`, `setupDevice` through `setupTestInterface`, and Linux netlink/procfs integration.

Risks: requires IPv6 sysctls and netlink privilege in the test namespace. Negative cases for invalid gateway and isolated mode are not covered.

Test signals: confirms the expected positive IPv6 setup path and catches regressions where IPv6 remains disabled or the requested bridge address is not programmed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_ipv6_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux.go

Purpose: Verifies an existing Linux bridge matches IPv4 configuration and checks whether an interface name resolves to a bridge.

Important APIs and functions: `setupVerifyAndReconcileIPv4` skips isolated IPv4 gateway mode, obtains `FAMILY_V4` addresses through `bridgeInterface.addresses`, selects the configured address with `selectIPv4Address`, fails if no IPv4 address exists, and fails if a configured IPv4 address does not match the bridge. `bridgeInterfaceExists` uses `ns.NlHandle().LinkByName` and accepts only links whose type is `bridge`.

Control flow: verification is read-only except for logging through callers. Missing links matching netlink's "Link not found" string are converted to `(false, nil)`; other lookup errors are wrapped.

State and persistence: no persistent state. Reads kernel netlink state and returns validation errors.

Dependencies and integration points: used during bridge setup to decide whether an existing bridge can be reused. Depends on `ns.NlHandle`, `netlink`, and bridge address selection helpers.

Risks: detecting missing links by error string is brittle compared with typed errors. IPv4 validation checks IP equality but not mask equality. Isolated mode bypasses verification.

Test signals: `setup_verify_linux_test.go` covers matching address, mismatched address, and missing address; link-type checks are not directly covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux_test.go

Purpose: Tests bridge IPv4 verification behavior against a temporary Linux bridge.

Important APIs and functions: `setupVerifyTest` creates a `netlink.Bridge` named `default0` and returns a `bridgeInterface`. `TestSetupVerify` verifies success with the requested IPv4 address assigned. `TestSetupVerifyBad` expects failure for a different IPv4 address. `TestSetupVerifyMissing` expects failure when no IPv4 address exists.

Control flow: each test runs in a temporary OS network namespace, creates a bridge, optionally assigns an address, then calls `setupVerifyAndReconcileIPv4`.

State and persistence: manipulates only temporary namespace link/address state.

Dependencies and integration points: tests `setup_verify_linux.go` and netlink bridge address operations.

Risks: covers basic verification but not isolated gateway mode, mask mismatches, or `bridgeInterfaceExists` behavior.

Test signals: good regression coverage for the main error branches in IPv4 bridge verification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/setup_verify_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux.go

Purpose: Detects whether dockerd appears to run under WSL2 mirrored networking so bridge firewall code can apply WSL-specific loopback handling without executing external commands as root.

Important APIs and functions: `wslinfoPath` defaults to `/usr/bin/wslinfo` and is test-overridable. `isRunningUnderWSL2MirroredMode` returns true only when a `loopback0` link exists and `wslinfoPath` is a regular executable file.

Control flow: link lookup failures return false, except non-not-found errors are warned. File stat failures return false. The function uses mode bits instead of running `wslinfo --networking-mode`.

State and persistence: read-only; no persistent state.

Dependencies and integration points: depends on `nlwrap.LinkByName`, `netlink.LinkNotFoundError`, and containerd logging. Its result feeds bridge firewall workarounds for WSL2 mirrored mode.

Risks: heuristic can return false for unusual WSL installations without executable `wslinfo`, or true for environments that mimic `loopback0` plus executable `wslinfo`. The conservative design avoids privileged command execution.

Test signals: `wsl2_linux_test.go` covers loopback presence and executable/non-executable/no-file combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux_test.go

Purpose: Validates the WSL2 mirrored-mode detection heuristic in a temporary Linux namespace.

Important APIs and functions: `TestMirroredWSL2Workaround` table-drives four cases: no `loopback0`, valid mirrored simulation, non-executable `wslinfo`, and missing `wslinfo`. `simulateWSL2MirroredMode` creates a dummy `loopback0` and optionally points `wslinfoPath` at a temp executable.

Control flow: each subtest isolates network state, sets up simulated conditions, calls `isRunningUnderWSL2MirroredMode`, and restores `wslinfoPath` via cleanup.

State and persistence: mutates namespace link state and the package variable `wslinfoPath` only for the test duration.

Dependencies and integration points: depends on netlink dummy links and the implementation in `wsl2_linux.go`.

Risks: tests the heuristic, not real WSL2. It does not cover non-LinkNotFound netlink errors.

Test signals: gives focused coverage for the file-permission and loopback-gating behavior that prevents false positives.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/wsl2_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/host/host.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/host/host.go

Purpose: Implements Docker's built-in `host` network driver as a local, single-instance, mostly no-op driver that attaches containers to host networking semantics managed elsewhere.

Important APIs and types: `NetworkType` is `host`. `driver` stores the single network id under a mutex. `Register` registers local data and connectivity scope. `CreateNetwork` permits exactly one network and stores its id. `DeleteNetwork` always returns a forbidden error. Endpoint, join, leave, and operational-info methods are no-ops or empty maps. `Type` and `IsBuiltIn` identify the driver.

Control flow: the only guarded state transition is `CreateNetwork`, which rejects a second instance. Deletion is prohibited regardless of id.

State and persistence: in-memory `network` string only; no datastore persistence.

Dependencies and integration points: implements `driverapi.Driver`, integrates with libnetwork registration and `types.ForbiddenErrorf`/errdefs permission mapping.

Risks: by design there is no endpoint-level validation or cleanup. The single-instance guard is process-local and depends on daemon initialization creating the host network once.

Test signals: `host_test.go` covers type, first create, second-create rejection, and deletion rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/host/host.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/host/host_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/host/host_test.go

Purpose: Tests the minimal state and error contract of the host driver.

Important APIs and functions: `TestDriver` checks `Type`, successful first `CreateNetwork`, stored network id, forbidden second create, and forbidden `DeleteNetwork` for both existing and unknown ids.

Control flow: constructs the driver directly and calls public driver methods with a background context.

State and persistence: validates in-memory `driver.network`; no external state.

Dependencies and integration points: uses containerd errdefs to assert forbidden errors map to permission denied.

Risks: no coverage for register capabilities or endpoint/join no-op methods.

Test signals: confirms the key host-driver invariant: exactly one undeletable network.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/host/host_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan.go

Purpose: Defines the Linux ipvlan driver core constants, driver/network/endpoint state types, and registration entrypoint.

Important APIs and types: constants define interface name prefixes, `NetworkType`, option names (`parent`, `ipvlan_mode`, `ipvlan_flag`), modes (`l2`, `l3`, `l3s`), and flags (`bridge`, `private`, `vepa`). `driver` owns a datastore and a mutex-protected `networks` map. `endpoint` stores ids, MAC/IPs, source link name, and datastore metadata. `network` stores config and a mutex-protected endpoint map. `Register` initializes state from the datastore then registers with local data scope and global connectivity scope.

Control flow: registration builds the driver, calls `initStore` to repopulate networks/endpoints, and exposes the driver to libnetwork.

State and persistence: persistent state is owned by `ipvlan_store.go`; this file defines the objects holding runtime and DB metadata.

Dependencies and integration points: depends on `datastore`, `driverapi`, and libnetwork `scope`. Other ipvlan files implement the driverapi methods against these types.

Risks: driver registration fails if store restore fails. The driver has process-local runtime maps that must stay synchronized with datastore updates.

Test signals: `ipvlan_test.go` checks registration, nil-ish store initialization path, and type reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_endpoint.go

Purpose: Implements ipvlan endpoint creation and deletion, including IP/MAC validation, unsupported option warnings, datastore persistence, and netlink cleanup.

Important APIs and functions: `CreateEndpoint` validates ids, gets the network, rejects custom MAC addresses, records IPv4/IPv6 addresses from `InterfaceInfo`, warns for port mappings and exposed ports, persists the endpoint, and inserts it into the network. `DeleteEndpoint` validates ids, looks up the endpoint, deletes the generated source link if present, removes datastore state, and removes it from the network map.

Control flow: creation persists before adding to the in-memory endpoint map. Deletion best-effort removes kernel link and datastore record, logging cleanup failures except for the primary lookup/validation errors.

State and persistence: writes and deletes `endpoint` KV objects via `storeUpdate`/`storeDelete`; updates `network.endpoints`; deletes Linux links through `ns.NlHandle`.

Dependencies and integration points: integrates with libnetwork `InterfaceInfo`, netlabel port options, `types.PortBinding`, `types.TransportPort`, `errdefs.System`, and Linux netlink.

Risks: `ep.srcName` is not set until `Join`, so deleting an unjoined endpoint may look up an empty link name. Persistence happens before interface creation, so stale endpoint records are possible if later join fails and rollback does not delete.

Test signals: no direct endpoint tests in this subset; behavior is indirectly constrained by store and registration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_joinleave.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_joinleave.go

Purpose: Implements sandbox join behavior for ipvlan endpoints, creating the ipvlan link, configuring gateway/static-route behavior by mode, naming the container interface, and persisting the joined source name.

Important APIs and functions: `Join` starts an OpenTelemetry span, creates a unique source interface name, calls `createIPVlan`, stores `ep.srcName`, handles L3/L3S default connected routes and L2 gateway assignment/force-gateway semantics, disables gateway service, sets interface names with optional user interface name, and persists the endpoint. `Leave` is a no-op. `getSubnetForIP` finds matching same-mask subnets.

Control flow: mode-specific routing is skipped for internal networks. L3/L3S use connected default routes and disable gateway service; L2 chooses explicit gateways from IPAM or forces gateway flags if no gateway exists. The endpoint source name update is noted as not locked.

State and persistence: creates a Linux ipvlan link and records its name in the endpoint datastore. Updates `JoinInfo` with routes, gateway flags, and interface naming.

Dependencies and integration points: depends on `netutils.GenerateIfaceName`, `ns.NlHandle`, `driverapi.JoinInfo`, `netlabel.GetIfname`, libnetwork route types, and OpenTelemetry.

Risks: source-name mutation is not protected by the endpoint/network lock. If errors occur after link creation, cleanup depends on higher-level rollback paths. Gateway parsing assumes IPAM gateway strings are CIDR strings.

Test signals: no direct join tests in this subset; setup tests cover mode/flag conversion used by link creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_joinleave.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_network.go

Purpose: Implements ipvlan network create/delete, option parsing, IPAM processing, parent interface provisioning, and gateway allocation policy.

Important APIs and functions: `CreateNetwork` enforces kernel >= 4.2, rejects empty IPv4/IPv6 pools when enabled, parses options, processes IPAM, supplies a dummy parent when none is configured, calls `createNetwork`, and persists configuration. `createNetwork` rejects reuse of the same parent by a different network, creates dummy or VLAN parent links if missing, and adds runtime state. `GetSkipGwAlloc` always returns true for both families. `DeleteNetwork` deletes driver-created parent links, deletes endpoint links and datastore records, removes runtime state, and deletes the network config. `parseNetworkOptions`, `parseNetworkGenericOptions`, `newConfigFromLabels`, and `processIPAM` define config ingestion.

Control flow: create separates config parsing from link provisioning and datastore update; datastore failure rolls back only runtime network state, not necessarily created links. Existing same-id/same-parent restore returns an internal maskable error. Delete is best-effort for kernel cleanup but fails if network config deletion from datastore fails.

State and persistence: persists `configuration` and endpoint records in `ipvlan_store.go`; creates/deletes dummy and VLAN netlink devices when `CreatedSlaveLink` is true.

Dependencies and integration points: integrates with kernel version parser, netlabel flags, libnetwork IPAM data, netlink parent setup helpers, and `errdefs.InvalidParameter`.

Risks: parent uniqueness is stricter than macvlan and disallows sharing a parent across ipvlan networks. Type assertions on `EnableIPv4`/`EnableIPv6` assume booleans. Link creation may outlive datastore rollback.

Test signals: setup tests cover helper parsing and modes; no direct network create/delete tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup.go

Purpose: Provides Linux netlink helper functions for creating ipvlan interfaces, validating modes/flags, creating/deleting VLAN subinterfaces, creating/deleting dummy parent links, and deriving dummy names.

Important APIs and functions: `createIPVlan` maps mode and flag strings to netlink constants, verifies the parent, and creates `netlink.IPVlan`. `setIPVlanMode` maps `l2`, `l3`, `l3s`. `setIPVlanFlag` maps `bridge`, `private`, `vepa`. `parentExists` probes `ns.NlHandle`. `createVlanLink`/`delVlanLink` manage `parent.vid` links. `parseVlan` validates `name.vlan_id`. `createDummyLink`/`delDummyLink` manage dummy parent links. `getDummyName` returns `di-` plus a truncated network id.

Control flow: helpers generally validate naming and parent existence before mutating netlink state. VLAN IDs are restricted to 1-4094. Delete helpers avoid deleting parent devices by checking `ParentIndex`.

State and persistence: no datastore state; all effects are Linux netlink link creation, link up, or deletion.

Dependencies and integration points: used by ipvlan network and join code; depends on `vishvananda/netlink` through `ns.NlHandle`.

Risks: helper names and comments mention macvlan in a few error comments, but behavior is ipvlan. `createDummyLink` has an unused `truncNetID` parameter. Netlink operations require privilege and are not transactional.

Test signals: `ipvlan_setup_test.go` covers parent existence, VLAN parsing errors, mode mapping, and flag mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup_test.go

Purpose: Unit tests ipvlan setup helpers for interface existence, VLAN name parsing, mode conversion, and flag conversion.

Important APIs and functions: `TestValidateLink` checks `parentExists` on loopback and a fake interface. `TestValidateSubLink` checks valid `lo.10` and invalid formats/nonexistent parent. `TestSetIPVlanMode` checks l2/l3/l3s and invalid/empty modes. `TestSetIPVlanFlag` checks bridge/private/vepa and invalid/empty flags.

Control flow: tests are direct function calls with expected errors and netlink constants.

State and persistence: reads host loopback link; no datastore. It does not create links.

Dependencies and integration points: depends on `netlink` constants and the setup helper implementations.

Risks: uses real namespace `lo`, so unusual test environments without loopback would fail. Does not test actual link creation/deletion.

Test signals: good coverage for pure validation and mapping logic, weaker coverage for privileged netlink mutations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_state.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_state.go

Purpose: Provides concurrency-safe runtime state accessors for ipvlan networks and endpoints plus shared id validation.

Important APIs and functions: `driver.network`, `addNetwork`, `deleteNetwork`, `getNetworks`, `network.endpoint`, `addEndpoint`, `deleteEndpoint`, `validateID`, and `driver.getNetwork`.

Control flow: driver-level methods lock `driver.mu` around `networks`. Network-level methods lock `network.mu` around `endpoints`. `network` logs and returns nil when missing; `getNetwork` returns typed libnetwork errors.

State and persistence: manipulates in-memory maps only. Persistent state is handled separately in `ipvlan_store.go`.

Dependencies and integration points: called throughout network, endpoint, and join/leave paths. Uses `types.InvalidParameterErrorf` and `types.NotFoundErrorf` for public error semantics.

Risks: there are two lookup styles with different error behavior. Callers must choose carefully. Some endpoint field mutations after lookup are not protected by the map lock.

Test signals: no direct state tests; behavior is indirectly exercised by registration and higher-level driver operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_store.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_store.go

Purpose: Implements ipvlan datastore persistence for network configurations and endpoints, including restore, stale endpoint cleanup, custom JSON formats, and `datastore.KVObject` methods.

Important APIs and types: constants define key prefixes. `configuration` stores network options, IPAM subnets, internal state, and DB metadata. `ipSubnet` stores subnet and gateway strings. `initStore`, `populateNetworks`, and `populateEndpoints` restore persisted objects. `storeUpdate` and `storeDelete` wrap datastore atomic put/delete. `configuration` and `endpoint` implement JSON marshal/unmarshal and KV object methods.

Control flow: init restores networks first so endpoint restoration can attach to existing runtime networks. Endpoints whose network is absent are deleted as stale. Missing store keys are treated as empty state. A nil store logs and makes persistence a no-op.

State and persistence: keys are `ipvlan/network/<id>` and `ipvlan/endpoint/<id>`. Config JSON stores nested subnets as JSON-encoded strings and migrates missing `IpvlanFlag` to `bridge`.

Dependencies and integration points: integrates with libnetwork `datastore`, `types.ParseCIDR`, and network creation via `d.createNetwork`.

Risks: unmarshal uses unchecked type assertions, so corrupted datastore JSON can panic. Endpoint keys are only by endpoint id, assuming global uniqueness. Restore can recreate links and may log but continue on per-network failures.

Test signals: `ipvlan_test.go` checks `initStore` with temp store but does not validate JSON compatibility or stale cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_test.go

Purpose: Tests ipvlan driver registration and basic type behavior.

Important APIs and functions: `driverTester` validates `RegisterDriver` receives name `ipvlan` and a `*driver`, and fails if a network allocator is unexpectedly registered. `TestIpvlanRegister`, `TestIpvlanNilConfig`, and `TestIpvlanType` exercise registration, store initialization, and `Type`.

Control flow: each test uses `storeutils.NewTempStore`, calls `Register`, and inspects the captured driver.

State and persistence: uses an empty temporary datastore; does not create networks.

Dependencies and integration points: verifies integration with libnetwork registration and temp datastore utilities.

Risks: no coverage for network lifecycle, endpoint lifecycle, join routing, or datastore restore with populated records.

Test signals: confirms the driver wires into registration correctly and can initialize with an empty store.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan.go

Purpose: Defines the Linux macvlan driver constants, runtime types, and registration entrypoint.

Important APIs and types: constants define `NetworkType`, interface prefixes, macvlan modes (`private`, `vepa`, `bridge`, `passthru`), and option labels. `driver` owns datastore and mutex-protected networks. `endpoint` stores ids, MAC/IPs, source name, and datastore metadata. `network` stores config and endpoint map. `Register` restores datastore state and registers the driver with local data scope and global connectivity.

Control flow: registration mirrors ipvlan: construct driver, `initStore`, register driver.

State and persistence: runtime maps are defined here; datastore format is in `macvlan_store.go`.

Dependencies and integration points: integrates with `driverapi`, `datastore`, and scope constants. Sibling files implement lifecycle behavior.

Risks: runtime maps and datastore must remain consistent across partial failures. Macvlan mode and parent sharing rules are enforced outside this core file.

Test signals: `macvlan_test.go` covers registration and type reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_endpoint.go

Purpose: Implements macvlan endpoint create/delete, including MAC assignment, unsupported option warnings, datastore persistence, and netlink interface cleanup.

Important APIs and functions: `CreateEndpoint` validates ids, gets the network, records IP addresses and optional MAC, generates and assigns a random MAC if absent, warns for port mappings and exposed ports, stores the endpoint, and adds it to the network. `DeleteEndpoint` looks up the endpoint, deletes its source link if present, removes datastore state, and removes runtime state.

Control flow: MAC generation happens before persistence. Persistence precedes runtime insertion. Delete logs netlink and store cleanup failures but removes runtime endpoint state.

State and persistence: writes/deletes endpoint KV records and updates `network.endpoints`; deletes Linux macvlan source interfaces by name.

Dependencies and integration points: depends on libnetwork `InterfaceInfo`, `netutils.GenerateRandomMAC`, netlabel port/expose options, `errdefs.System`, and Linux netlink.

Risks: deleting before join may attempt lookup of an empty source name. Persisting before join can leave stale endpoint records if later join fails without rollback. Port mapping is only warned, not rejected.

Test signals: no direct endpoint tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_joinleave.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_joinleave.go

Purpose: Implements macvlan sandbox join behavior by creating a macvlan link, selecting gateways from IPAM, setting interface names, disabling gateway service, and persisting the endpoint's source name.

Important APIs and functions: `Join` creates a unique source name, calls `createMacVlan`, records `ep.srcName`, configures IPv4/IPv6 gateway or force-gateway flags when not internal, disables gateway service, sets names through `JoinInfo.InterfaceName`, and persists the endpoint. `Leave` is a no-op. `getSubnetForIP` matches endpoint address to configured subnets by mask and containment.

Control flow: internal networks skip gateway configuration. Missing IPAM gateway forces gateway flags to preserve external-connectivity semantics. Interface name setting honors `netlabel.GetIfname`.

State and persistence: creates Linux macvlan links and persists the updated endpoint source name. Mutates `JoinInfo` route/gateway/interface fields.

Dependencies and integration points: depends on `netutils.GenerateIfaceName`, `createMacVlan`, `driverapi.JoinInfo`, and OpenTelemetry tracing.

Risks: `ep.srcName` update is not locked. Errors after link creation require caller rollback to clean up. Gateway strings are parsed as CIDR.

Test signals: no direct join tests; setup tests cover mode conversion and VLAN parsing used by join/network.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_joinleave.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_network.go

Purpose: Implements macvlan network creation/deletion, parent interface provisioning, option parsing, IPAM processing, and gateway allocation behavior.

Important APIs and functions: `CreateNetwork` rejects empty enabled IP pools, parses options, processes IPAM, supplies dummy parent when missing, calls `createNetwork`, and persists config. `GetSkipGwAlloc` returns true for both families. `createNetwork` allows shared parents except when any involved network uses passthru mode, creates dummy/VLAN parents, and marks shared driver-created links. `parentHasSingleUser` gates deletion of shared created parents. `DeleteNetwork` cleans endpoint links and datastore records, conditionally deletes parent link, and removes config. Parsing helpers map labels to config and subnets.

Control flow: create handles existing same-id network as restore via internal maskable error. Delete only removes driver-created parent links when this network is the last user, unlike ipvlan.

State and persistence: persists network configs/endpoints through store helpers and creates/deletes Linux dummy or VLAN links.

Dependencies and integration points: uses netlabel options, libnetwork IPAM, `types.InternalMaskableErrorf`, and setup helpers.

Risks: type assertions on enable flags assume booleans. Link creation can outlive datastore rollback. Parent sharing requires accurate `CreatedSlaveLink` propagation to avoid deleting links still in use.

Test signals: no direct network lifecycle tests; setup and registration tests cover smaller pieces.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup.go

Purpose: Provides Linux netlink helper functions for macvlan link creation, mode mapping, VLAN subinterface management, dummy parent link management, and dummy name derivation.

Important APIs and functions: `createMacVlan` maps mode strings to netlink constants, verifies the parent, and creates `netlink.Macvlan`. `setMacVlanMode` maps private/vepa/bridge/passthru. `parentExists`, `createVlanLink`, `delVlanLink`, `parseVlan`, `createDummyLink`, `delDummyLink`, and `getDummyName` implement parent link support.

Control flow: VLAN creation parses `parent.vlan`, validates VLAN ID 1-4094, creates and brings up the VLAN link. Delete verifies the link is a slave before removal. Dummy deletion verifies `ParentIndex == 0`.

State and persistence: mutates only Linux link state; persistence is handled by network/store code.

Dependencies and integration points: used by macvlan network and join paths; depends on `vishvananda/netlink` and `ns.NlHandle`.

Risks: netlink operations are not transactional. `createDummyLink` has an unused second parameter. Real parent and VLAN operations need privilege.

Test signals: `macvlan_setup_test.go` covers validation and mode mapping, not actual link creation/deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup_test.go

Purpose: Tests macvlan setup helper validation and mode mapping.

Important APIs and functions: `TestValidateLink` checks `parentExists`. `TestValidateSubLink` checks valid and invalid VLAN naming/parent cases. `TestSetMacVlanMode` checks bridge, passthru, private, vepa, invalid, and empty mode conversions.

Control flow: direct assertions on helper return values and netlink constants.

State and persistence: reads interface existence; no datastore and no link creation.

Dependencies and integration points: verifies `macvlan_setup.go` helper behavior against `netlink` constants.

Risks: depends on loopback interface existing. Does not cover privileged netlink mutations or dummy-name generation.

Test signals: focused validation coverage for setup helper pure logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_state.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_state.go

Purpose: Provides concurrency-safe runtime state helpers for macvlan networks and endpoints plus id validation.

Important APIs and functions: `driver.network`, `addNetwork`, `deleteNetwork`, `getNetworks`, `network.endpoint`, `addEndpoint`, `deleteEndpoint`, `validateID`, and `driver.getNetwork`.

Control flow: driver methods lock `driver.mu`, network methods lock `network.mu`, and `getNetwork` returns typed libnetwork errors for public paths.

State and persistence: manipulates in-memory maps only; persistent state is handled in `macvlan_store.go`.

Dependencies and integration points: called by macvlan network, endpoint, and join paths.

Risks: missing-network `network` logs and returns nil, while `getNetwork` returns errors; inconsistent use can affect caller behavior. Endpoint object field mutation after lookup is not fully protected.

Test signals: no direct state tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_store.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_store.go

Purpose: Implements datastore persistence for macvlan network configurations and endpoints, including restore, stale endpoint cleanup, custom JSON, and `datastore.KVObject` methods.

Important APIs and types: key prefixes are `macvlan/network` and `macvlan/endpoint`. `configuration` stores ID, MTU, internal flag, parent, mode, created-link flag, and IPv4/IPv6 subnets. `ipSubnet` stores subnet/gateway strings. `initStore`, `populateNetworks`, `populateEndpoints`, `storeUpdate`, and `storeDelete` manage persistence. `configuration` and `endpoint` marshal/unmarshal JSON and implement KV object methods.

Control flow: restores networks before endpoints; deletes stale endpoints whose networks are absent. Nil store makes update/delete a logged no-op.

State and persistence: config and endpoint records are JSON blobs under driver-specific prefixes. Subnet slices are JSON-encoded strings inside the outer JSON map.

Dependencies and integration points: uses `datastore`, `types.ParseCIDR`, and `d.createNetwork` for restore side effects.

Risks: unchecked JSON type assertions can panic on corrupt store data. Endpoint keys use endpoint id only. Restore of a network can create links and log warnings without stopping all restore.

Test signals: registration tests initialize an empty temp store but do not validate populated restore or migration behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_test.go

Purpose: Tests macvlan driver registration and type reporting.

Important APIs and functions: `driverTester` validates `RegisterDriver` receives `macvlan` and a `*driver`, while `RegisterNetworkAllocator` is unexpected. `TestMacvlanRegister`, `TestMacvlanNilConfig`, and `TestMacvlanType` cover registration, empty-store init, and `Type`.

Control flow: tests use a temp datastore and capture the registered driver.

State and persistence: uses empty temp store; no network records are created.

Dependencies and integration points: checks libnetwork registration contract.

Risks: no coverage for create/delete, endpoint, join, parent sharing, or store restore.

Test signals: verifies basic driver wiring only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/null/null.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/null/null.go

Purpose: Implements Docker's built-in `null` network driver as a local single-instance, no-connectivity driver.

Important APIs and types: `NetworkType` is `null`. `driver` stores a single network id under a mutex. `Register` registers local data scope. `CreateNetwork` allows exactly one network. `DeleteNetwork` always returns forbidden. Endpoint create/delete, join/leave, and operational info are no-ops or empty maps. `Type` and `IsBuiltIn` identify the driver.

Control flow: matches host driver except no explicit connectivity scope is registered. Deletion is always prohibited.

State and persistence: in-memory `network` string only.

Dependencies and integration points: integrates with libnetwork driver registration and typed forbidden errors.

Risks: intentionally no endpoint-level behavior; correctness depends on higher layers using the null network as non-connective.

Test signals: `null_test.go` covers type, single-instance create, and deletion rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/null/null.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/null/null_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/null/null_test.go

Purpose: Tests the null driver's single-network and undeletable-network contract.

Important APIs and functions: `TestDriver` checks `Type`, first `CreateNetwork`, stored id, forbidden second create, and forbidden delete for known/unknown ids.

Control flow: direct calls against a local `driver` value.

State and persistence: validates only in-memory state.

Dependencies and integration points: uses containerd errdefs to check permission-denied classification.

Risks: does not test registration capabilities or no-op endpoint/join methods.

Test signals: confirms the key invariants of the null driver.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/null/null_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf.go

Purpose: Builds classic BPF bytecode and iptables match fragments for matching VXLAN datagrams by VNI.

Important APIs and functions: `vniMatchBPF` assembles a cBPF program that loads UDP payload offset, reads the VXLAN VNI field at payload offset 4, shifts off reserved bits, compares to the requested VNI, and returns match/no-match. `marshalXTBPF` serializes raw BPF instructions for `iptables -m bpf --bytecode`. `matchVXLAN` returns an iptables argument fragment for UDP destination port and BPF VNI match.

Control flow: BPF assembly panics only if static instructions are invalid. `matchVXLAN` creates a fresh argument slice so callers can append safely.

State and persistence: stateless helper; no kernel mutation itself.

Dependencies and integration points: used by overlay encryption firewall rules to mark outgoing encrypted VXLAN and drop incoming cleartext VXLAN. Depends on `golang.org/x/net/bpf` and iptables bpf match support.

Risks: cBPF depends on Linux payload-offset extension and xt_bpf behavior. VNI values are accepted as uint32 even though VXLAN VNI is 24 bits; callers often mask or validate elsewhere.

Test signals: `bpf_linux_test.go` attaches the program as a raw socket filter, and `bpf_test.go` fuzzes assembly panic safety.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_linux_test.go

Purpose: Linux integration test for the VNI-matching cBPF program using raw IPv4 UDP loopback traffic.

Important APIs and functions: `TestVNIMatchBPF` reserves a UDP port, opens a raw IPv4 UDP socket, attaches `vniMatchBPF`, sends VXLAN-like payloads, and verifies only matching VNIs pass. Helpers build VXLAN headers, attach filters, drain sockets, read matching UDP packets, and parse IPv4/UDP headers.

Control flow: skips when raw socket creation returns `EPERM`. For each tested VNI, it sends multiple vector VNIs and compares receipt to equality with the filter VNI.

State and persistence: attaches socket filters to a temporary raw socket only.

Dependencies and integration points: depends on Linux raw sockets, `ipv4.PacketConn.SetBPF`, and BPF helper output from `bpf.go`.

Risks: requires `CAP_NET_RAW`; loopback traffic from unrelated processes is filtered but can add noise. It covers IPv4 raw socket behavior, not iptables xt_bpf or IPv6 directly.

Test signals: strong practical signal that the bytecode selects the expected VXLAN VNI values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_test.go

Purpose: Fuzzes `vniMatchBPF` over representative and arbitrary VNI inputs to ensure it does not panic.

Important APIs and functions: `FuzzVNIMatchBPFDoesNotPanic` seeds boundary-ish uint32 values and calls `vniMatchBPF` for fuzzed inputs.

Control flow: fuzz target ignores output and checks panic-free assembly.

State and persistence: stateless.

Dependencies and integration points: covers the non-Linux-safe part of BPF program construction.

Risks: does not verify semantic matching; that is handled by Linux raw socket test.

Test signals: catches future instruction-construction changes that make BPF assembly invalid for some input.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption.go

Purpose: Implements Linux encrypted overlay data-plane support using IPsec/XFRM transport mode plus firewall rules that force VXLAN traffic for secure VNIs through encryption.

Important APIs and types: constants define XFRM mark and ESP packet expansion. `key`, `spi`, `encrNode`, and `encrMap` model encryption keys and per-peer SAs. `setupEncryption` programs reverse SAs for all keys and bidirectional SA/SP for the primary key. `removeEncryption` reference-counts peers and removes SAs/SPs. `programMangle`, `programInput`, and `programOverlayEncryptionFirewall` manage iptables/nftables firewall enforcement. `programSA`, `programSP`, `saExists`, `spExists`, `buildSPI`, and `buildAeadAlgo` manipulate XFRM state/policies. `setKeys`, `updateKeys`, `updateNodeKey`, `maxMTU`, and `clearEncryptionStates` manage key lifecycle and cleanup.

Control flow: encryption setup requires keys and uses `encrMu`; primary key is index 0. Key rotation can add a key, promote primary, and prune old keys while updating per-node XFRM objects in an order intended to maintain connectivity. Firewall programming uses nftables when enabled, otherwise iptables mangle/filter rules. Failure to determine transport table fails closed for encrypted setup.

State and persistence: no datastore. Kernel XFRM state/policies and iptables/nftables rules are persistent kernel side effects until cleanup. In-memory `secMap` tracks peer counts and SPI lists; `keys` holds active key material.

Dependencies and integration points: used by overlay peer add/delete and network subnet initialization. Depends on netlink XFRM, overlayutils VXLAN port, iptables, nftables, discovery encryption notifications, and driver bind/advertise addresses.

Risks: high side-effect surface with partial failure logging. `programSP` assumes forward/reverse SA pointers are non-nil for primary operations. Key strings reveal a short key prefix in debug output. Correctness depends on lock hierarchy and on matching advertise/bind address families. Packet MTU calculation must match ESP overhead.

Test signals: `encryption_test.go` verifies SPI compatibility with legacy hashing for IPv4/IPv6 forms; there are no full XFRM programming integration tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_nft_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_nft_linux.go

Purpose: Implements nftables enforcement for encrypted overlay VNIs as an alternative to legacy iptables rules.

Important APIs and functions: constants define table, chain, set names, and the VXLAN VNI expression. `ensureOverlayEncNftTable` lazily creates the `docker-overlay` table, encrypted VNI set, output route chain that marks matching VXLAN packets, and input raw chain that drops unencrypted matching VXLAN packets. `programOverlayEncVNINft` cleans stale iptables rules, ensures the table, then adds or deletes a VNI set element. `cleanupNft` deletes the entire overlay table on startup when nftables is not the active backend.

Control flow: table creation is protected by `overlayEncNftInitMu` and cached in `overlayEncNftTable`. VNI elements are formatted as 24-bit hex with `vni&0xffffff`.

State and persistence: mutates nftables kernel ruleset and caches an nftables table handle in the driver.

Dependencies and integration points: called from `programOverlayEncryptionFirewall`; depends on `nftables` internal package, `overlayutils.VXLANUDPPort`, and `driver.isIPv6Transport`.

Risks: stale iptables cleanup failures are logged but not fatal. If transport address is unknown, table setup fails. Cached table validity must reflect actual nftables state.

Test signals: no direct nftables tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_nft_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_test.go

Purpose: Verifies `buildSPI` remains compatible with the legacy FNV-based SPI derivation across IPv4, IPv4-mapped IPv6, and IPv6 inputs.

Important APIs and functions: `legacyBuildSPI` hashes source IP, key tag, and destination IP using `fnv.New32a`. `TestBuildSPI` compares `buildSPI` against legacy results for multiple address combinations and also checks unmapped forms.

Control flow: table-driven assertions build expected values with `net.ParseIP` and actual values with `netip.Addr`.

State and persistence: stateless.

Dependencies and integration points: protects compatibility for XFRM SA identifiers in `encryption.go`.

Risks: only covers SPI derivation, not XFRM programming, firewall rules, or key rotation.

Test signals: strong compatibility signal for a low-level value that must remain stable across daemon versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/joinleave.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/joinleave.go

Purpose: Implements Linux overlay endpoint join/leave and NetworkDB table event handling for peer discovery.

Important APIs and functions: `Join` validates ids, locks the network, checks secure-key/XFRM support, initializes the network/subnet sandbox, creates a veth pair, sets MTU and MAC, attaches one side to the overlay sandbox bridge, configures static routes for other subnets, sets container interface names, adds the local peer to peer DB, and publishes a `PeerRecord` through `JoinInfo.AddTableEntry`. `DecodeTableEntry` decodes peer records for display. `EventNotify` applies NetworkDB peer add/delete updates while ignoring local peers and no-op updates. `Leave` removes the local peer and decrements sandbox join state.

Control flow: network lock guards endpoint lookup, sandbox state, and peer DB changes. Event handling unmarshals previous and new values, filters local peers, then does differential delete/add.

State and persistence: no datastore. Mutates kernel veth, bridge, VXLAN, neighbor/FDB, XFRM/firewall state through downstream calls and updates in-memory network/peer state.

Dependencies and integration points: central integration with `driverapi.JoinInfo`, NetworkDB table watcher, `PeerRecord` protobuf, overlay peerdb, OSL sandbox, netlink, and encryption.

Risks: large partial-failure surface during join after sandbox/link creation. Secure networks fail if keys or XFRM family support are unavailable. Static-route error logs but does not fail join.

Test signals: no direct join tests in this subset; overlay registration and peer/proto support are covered separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/joinleave.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_linux.go

Purpose: Applies Linux neighbor table sysctl tuning for overlay scalability.

Important APIs and functions: `ovConfig` defines `net.ipv4.neigh.default.gc_thresh1/2/3` target values with `checkHigher`. `checkHigher` returns true when the current value is lower than the target. `applyOStweaks` delegates to `kernel.ApplyOSTweaks`.

Control flow: called once by overlay driver configuration. Values are only raised when lower.

State and persistence: mutates host/kernel sysctl state through `kernel.ApplyOSTweaks`; no datastore.

Dependencies and integration points: used by `driver.configure` in `overlay.go`.

Risks: parse errors in `checkHigher` are ignored as zero, which may treat invalid values as needing update. Sysctl writes may fail in restricted environments.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_unsupported.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_unsupported.go

Purpose: Provides a non-Linux no-op implementation of overlay OS tuning.

Important APIs and functions: `applyOStweaks` is an empty function under `!linux`.

Control flow: allows cross-platform builds of overlay package components without Linux sysctl dependencies.

State and persistence: none.

Dependencies and integration points: selected by build tags as the counterpart to `ostweaks_linux.go`.

Risks: non-Linux platforms do not receive equivalent tuning; this is intentional.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_endpoint.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_endpoint.go

Purpose: Implements Linux overlay endpoint create/delete and operational-info behavior.

Important APIs and types: `endpointTable` maps endpoint ids. `endpoint` stores id, network id, interface name, MAC, and IP prefix. `CreateEndpoint` lazily configures the driver, locks the network, validates endpoint IP and subnet, uses supplied MAC or generates one from IP, sets MAC in `InterfaceInfo`, and inserts runtime endpoint state. `DeleteEndpoint` removes runtime endpoint state and deletes the container-side veth if it was created. `EndpointOperInfo` returns an empty map.

Control flow: create validates subnet membership before storing endpoint. Delete tolerates missing Linux link by logging debug and returning nil after endpoint removal.

State and persistence: runtime only; no datastore. Delete mutates kernel link state if `ep.ifName` is known.

Dependencies and integration points: integrates with `driver.configure`, `lockNetwork`, `netiputil`, `hashable.MACAddr`, netlink, and libnetwork `InterfaceInfo`.

Risks: no persistent endpoint restore; overlay relies on cluster state and runtime reconstruction. Generated MAC from IP assumes helper returns MAC-48; panic if not. Deleting runtime state before link deletion can leave kernel residue if deletion fails.

Test signals: no direct endpoint tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_network.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_network.go

Purpose: Implements Linux overlay network lifecycle, lazy sandbox/subnet initialization, VXLAN/bridge creation, stale sandbox cleanup, and network locking.

Important APIs and types: `network`, `subnet`, and global `vniTbl` model overlay networks and VNI ownership. `CreateNetwork` validates IPv4 IPAM and VNI options, parses secure/MTU options, stores subnets, publishes the network under lock, cleans stale encryption rules for non-secure networks, and registers the peer table. `DeleteNetwork` cleans endpoint links, encryption firewall rules, and removes the network. `joinSandbox`, `leaveSandbox`, `destroySandbox`, `populateVNITbl`, name generators, `setupSubnetSandbox`, `setDefaultVLAN`, `initSubnetSandbox`, `cleanupStaleSandboxes`, `initSandbox`, `lockNetwork`, and `getSubnetforIP` manage the lazy network namespace.

Control flow: overlay resources are created lazily on first join. Global VNI table is populated once from existing namespace paths to reclaim stale VXLANs. Network object locking avoids driver/network lock inversion by double-checking active map entries. Sandbox teardown happens when join count reaches zero.

State and persistence: no datastore. Mutates OSL network namespaces, Linux bridges, VXLAN links, sysfs bridge VLAN settings, encryption firewall state, endpoint links, and in-memory tables.

Dependencies and integration points: integrates with libnetwork IPAM/options, `overlayutils.AppendVNIList`, OSL sandbox, netlink/netns, nftables/iptables encryption helpers, and NetworkDB peer table registration.

Risks: many kernel side effects can partially fail. `setDefaultVLAN` uses mount namespace operations on a locked OS thread. Stale sandbox cleanup uses name-pattern matching and must avoid deleting current resources. `CreateNetwork` type-asserts generic options.

Test signals: no direct lifecycle tests in this subset; ovmanager tests cover VNI allocation separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_utils.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_utils.go

Purpose: Provides Linux overlay utility helpers for id validation, veth creation, VXLAN creation/deletion, and VNI-based VXLAN cleanup.

Important APIs and functions: `validateID` checks network and endpoint ids. `createVethPair` generates two veth names and creates a `netlink.Veth`. `createVxlan` creates a VXLAN link with learning/proxy/L2miss/L3miss enabled and configurable UDP port; it sets IPv6 unspecified group when VTEP addresses are IPv6. `deleteInterface` deletes a named link. `deleteVxlanByVNI` can operate in a specified network namespace and delete the first matching VXLAN by VNI or any VXLAN when VNI is zero.

Control flow: namespace-specific VXLAN deletion opens a netns handle and netlink handle with socket timeout, lists links, and deletes matching VXLAN.

State and persistence: mutates Linux link state; no datastore.

Dependencies and integration points: used by overlay join/network cleanup. Depends on `netutils`, `netlink`, `netns`, `nlwrap`, and `overlayutils.VXLANUDPPort`.

Risks: `deleteVxlanByVNI` deletes only the first matching VXLAN. Link generation and creation can race with other processes. VXLAN VTEP family must match peer family.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ov_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.go

Purpose: Defines the Linux overlay driver core, registration, one-time OS configuration, transport address discovery, and discovery event handling.

Important APIs and types: constants define `NetworkType`, veth naming, VXLAN encapsulation overhead, and `secureOption`. `driver` stores OS init, encryption state, nftables table cache, bind/advertise addresses, and network table with explicit lock hierarchy. `Register` registers global data/connectivity scope. `configure` applies OS tweaks and cleans nftables if using iptables. `isIPv6Transport` infers VTEP family from advertise address. `nodeJoin` records self discovery bind/advertise addresses. `DiscoverNew` handles node discovery, initial encryption keys, and key updates. `DiscoverDelete` is currently no-op.

Control flow: configuration is lazy and one-time. Discovery type switches validate payload types before updating driver state or encryption keys.

State and persistence: all state is in memory; kernel state is changed by `configure` and encryption helpers.

Dependencies and integration points: implements `discoverapi.Discover` and `driverapi.TableWatcher`, integrates with swarm discovery, encryption key distribution, nftables backend selection, and scope registration.

Risks: overlay transport cannot be configured until self discovery provides a valid advertise address; encryption setup depends on this. Lock hierarchy must be preserved across future changes.

Test signals: `overlay_test.go` covers registration and type only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.pb.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.pb.go

Purpose: Generated gogo/protobuf Go code for the overlay `PeerRecord` message used in NetworkDB peer table entries.

Important APIs and types: `PeerRecord` has `EndpointIP`, `EndpointMAC`, and `TunnelEndpointIP` string fields. Generated methods include proto reset/descriptor, getters, marshal/unmarshal, size, string/go-string, skip logic, and overflow/length errors.

Control flow: marshal writes non-empty string fields in reverse buffer order; unmarshal parses length-delimited fields 1-3 and skips unknown fields.

State and persistence: no runtime state. Serialized bytes are stored/transmitted through libnetwork's NetworkDB table entries.

Dependencies and integration points: produced from `overlay.proto` with gogofaster; used by Linux and Windows overlay join/event paths and `peer.go` parsing.

Risks: generated file should not be hand-edited. Schema changes require regenerating and preserving wire compatibility. Fields are strings, so semantic validation happens outside generated code.

Test signals: peer record use is indirectly exercised by join/event code; no direct generated-code tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.proto -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.proto

Purpose: Defines the protobuf schema for overlay peer records exchanged through NetworkDB.

Important APIs and types: `PeerRecord` contains `endpoint_ip`, `endpoint_mac`, and `tunnel_endpoint_ip` fields with gogo custom names `EndpointIP`, `EndpointMAC`, and `TunnelEndpointIP`. File options enable gogo marshaler, unmarshaler, stringer, go-string, and sizer generation while disabling standard Go proto stringer.

Control flow: schema is declarative; `overlay.pb.go` is generated from it.

State and persistence: serialized records represent endpoint-to-VTEP mappings in the overlay peer table.

Dependencies and integration points: imported by generated Go code and used by Linux/Windows overlay join and event handling.

Risks: changing field numbers or meanings breaks NetworkDB compatibility. String fields require downstream parsing and validation.

Test signals: no direct proto tests; generated code and peer unmarshal code consume this schema.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay_test.go

Purpose: Tests Linux overlay driver registration and type reporting.

Important APIs and functions: `driverTester` validates `RegisterDriver` receives `overlay` and a `*driver`; plugin getter returns nil and network allocator registration is unexpected. `TestOverlayInit` checks registration succeeds. `TestOverlayType` checks `Type`.

Control flow: tests call `Register` with the fake registerer and inspect captured driver.

State and persistence: no kernel or datastore state.

Dependencies and integration points: verifies libnetwork registration contract for the overlay driver.

Risks: no coverage for network lifecycle, discovery, join, encryption, or peer events.

Test signals: basic smoke coverage for driver registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils.go

Purpose: Provides overlay utility functions for configuring the global VXLAN UDP port and parsing VNI CSV lists.

Important APIs and functions: `ConfigVXLANUDPPort` sets the package-global VXLAN port, defaulting zero to 4789 and allowing only 1024-49151. `VXLANUDPPort` reads the value under an RW mutex. `AppendVNIList` parses comma-separated uint32 decimal VNI values and appends them to a caller-provided slice.

Control flow: port configuration validates range before taking the write lock. VNI parsing preserves already-appended values on later parse errors.

State and persistence: global in-memory `vxlanUDPPort`; no datastore.

Dependencies and integration points: used by overlay VXLAN creation, firewall matching, encryption, and VNI allocation paths.

Risks: `AppendVNIList` does not enforce the 24-bit VXLAN VNI maximum; ovmanager enforces allocation bounds separately, but direct callers may accept larger values. Global port affects all overlay networks in process.

Test signals: `utils_test.go` covers parsing behavior and allocation count for VNI parsing, but not port configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils_test.go

Purpose: Tests `AppendVNIList` parsing, error handling, append semantics, and allocation behavior.

Important APIs and functions: `TestAppendVNIList` checks nil/empty/existing slices, trailing comma, invalid tokens, and a zero-allocation reuse scenario.

Control flow: table-driven tests compare returned slices and expected error substrings. The allocation subtest reuses a preallocated slice in `testing.AllocsPerRun`.

State and persistence: stateless except local slices.

Dependencies and integration points: protects utility behavior used by overlay driver and ovmanager option parsing.

Risks: does not validate VNI range, because the function itself does not. Does not cover VXLAN UDP port configuration.

Test signals: good coverage for CSV parser behavior and performance expectation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager.go

Purpose: Implements the overlay network allocator responsible for assigning and freeing VXLAN IDs for overlay subnets.

Important APIs and types: `driver` owns a mutex-protected network table and bitmap allocator. VNI allocation range is 4096 through `(1<<24)-1`, avoiding VLAN ID overlap and respecting VXLAN maximum. `Register` registers a network allocator for `overlay`. `NetworkAllocate` parses user-specified VNI list, allocates missing VNIs per IPv4 subnet, stores network state, and returns the normalized `OverlayVxlanIDList`. `NetworkFree` releases all VNIs for a network. `releaseVxlanID` clears bitmap bits. `IsBuiltIn` returns true.

Control flow: user VNIs are consumed in subnet order; extra user VNIs are ignored in returned output beyond subnet count. Allocation failures roll back already-allocated IDs. Duplicate network ids are rejected after releasing new allocations.

State and persistence: in-memory bitmap and network map only; no datastore.

Dependencies and integration points: used by libnetwork's network allocation phase before overlay driver network creation. Depends on bitmap allocator, netlabel, and `overlayutils.AppendVNIList`.

Risks: bitmap size covers full VNI range, which is large but intended. User-specified VNIs below 4096 can be set because only auto-allocation avoids that range; this may be for compatibility but can conflict with Windows constraints.

Test signals: `ovmanager_test.go` covers auto allocation/free and user-defined VNIs with extra values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager_test.go

Purpose: Tests overlay VNI allocator behavior for automatic and user-defined allocations.

Important APIs and functions: `parseCIDR` builds IPAM pools. `TestNetworkAllocateFree` allocates two subnets and confirms two returned VNI IDs, then frees the network. `TestNetworkAllocateUserDefinedVNIs` supplies three VNIs for two subnets and verifies the returned list contains exactly the first two.

Control flow: tests use `newDriver` directly and inspect returned option map.

State and persistence: in-memory allocator only.

Dependencies and integration points: validates `NetworkAllocate`/`NetworkFree` and netlabel VNI option output.

Risks: does not test duplicate VNI rejection, duplicate network ids, allocation exhaustion, or invalid VNI parse errors.

Test signals: useful coverage for common allocation paths and normalized output count.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ovmanager/ovmanager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peer.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peer.go

Purpose: Defines the overlay peer table name, typed peer model, and protobuf decoding/validation for peer records.

Important APIs and types: `OverlayPeerTable` is `overlay_peer_table`. `Peer` stores endpoint IP prefix, endpoint MAC, and tunnel endpoint IP. `UnmarshalPeerRecord` unmarshals `PeerRecord` bytes and parses/validates IP prefix, MAC, and VTEP address.

Control flow: any protobuf or semantic parse error is wrapped with field-specific context.

State and persistence: no state. Converts NetworkDB table bytes into typed peer data.

Dependencies and integration points: used by Linux and Windows overlay `EventNotify` handlers. Depends on gogo/protobuf and internal `hashable` types.

Risks: invalid remote data is rejected and logged by callers. String schema means validation is deferred to this boundary.

Test signals: no direct peer parsing tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peerdb.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peerdb.go

Purpose: Maintains overlay peer database state and programs Linux neighbor/FDB/XFRM entries for remote overlay peers.

Important APIs and types: `peerEntry` stores endpoint id, MAC, and VTEP, with invalid VTEP meaning local. `peerMap` wraps a set-matrix allowing transient multiple entries per IP. `Walk`, `Get`, `Add`, and `Delete` manage peer entries. `network.initSandboxPeerDB` replays remote peers into a newly initialized sandbox. `peerAdd`/`peerDelete` update DB and kernel state. `addNeighbor` adds neighbor and bridge FDB entries, starts encryption for secure networks, and joins subnets lazily. `deleteNeighbor` removes encryption, FDB, and neighbor entries with reference counting.

Control flow: duplicate IP conditions are logged as transient. If a delete leaves another DB entry for the same IP, it restores one kernel configuration. FDB entries are reference-counted by VTEP+MAC to avoid premature deletion.

State and persistence: in-memory peer DB and FDB count map; kernel neighbor/FDB entries in the overlay sandbox; XFRM encryption state through driver encryption helpers.

Dependencies and integration points: driven by NetworkDB events from `joinleave.go`; depends on OSL namespace neighbor APIs, `hashable`, `setmatrix`, and encryption.

Risks: transient duplicate handling is complex and can mask failures in expected races. Encryption setup/removal errors are logged but not fatal. Correctness depends on caller holding the network lock.

Test signals: no direct peerdb tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/peerdb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/remote/api/api.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/remote/api/api.go

Purpose: Defines the JSON request/response structs for Docker remote network driver plugin RPCs.

Important APIs and types: `Response`/`GetError` provide common plugin error propagation. Capability, network allocate/free, gateway allocation check, create/delete network, create/delete endpoint, endpoint info, join/leave, external connectivity, revoke connectivity, and discovery notification request/response structs model all supported plugin methods. `EndpointInterface`, `InterfaceName`, and `StaticRoute` represent endpoint and join data.

Control flow: declarative transport contract; `remote/driver.go` serializes these structs through the plugin client.

State and persistence: no runtime state. These structs are wire-contract state exchanged with external plugins.

Dependencies and integration points: ties plugin API to libnetwork `driverapi.IPAMData`, `discoverapi.DiscoveryType`, and `types.RouteType`.

Risks: field names and shapes are plugin API compatibility surface. `DiscoveryData any` relies on JSON encoding preserving useful shape for plugins.

Test signals: `remote/driver_test.go` exercises many request/response shapes through an HTTP test plugin.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/remote/api/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver.go

Purpose: Implements the adapter between libnetwork's driver interfaces and external network driver plugins.

Important APIs and types: `driver` stores plugin client, network type, gateway-allocation capability, and endpoint gateway state. `Register` discovers active plugins, negotiates capabilities, registers drivers, and registers network allocators for global data scope. `getPluginClient` handles v1 clients or HTTP v1 plugin addresses. `getCapabilities`, `call`, `NetworkAllocate`, `NetworkFree`, `CreateNetwork`, `GetSkipGwAlloc`, `DeleteNetwork`, `CreateEndpoint`, `DeleteEndpoint`, `EndpointOperInfo`, `Join`, `Leave`, `ProgramExternalConnectivity`, `revokeExternalConnectivity`, `DiscoverNew`, `DiscoverDelete`, `parseStaticRoutes`, and `parseInterface` implement the API mapping.

Control flow: plugin method names are prefixed with `NetworkDriver.`. Plugin response `Err` fields become errors. CreateEndpoint and Join have rollback defers that call DeleteEndpoint/Leave if applying plugin-returned state fails. ProgramExternalConnectivity tracks gateway identity and passes `NoProxy6To4` when another endpoint handles IPv6.

State and persistence: no datastore. In-memory `nwEndpoints` tracks joined endpoints and gateway status for external connectivity calls. External plugin owns its own persistence.

Dependencies and integration points: central integration with Docker plugin system, libnetwork driverapi/network allocator/discovery interfaces, netlabel options, and API structs.

Risks: endpoint map is keyed only by endpoint id, not network id. Rollback error wrapping order can be confusing. Plugin compatibility requires tolerating missing external connectivity methods. `Join` ignores `DstName` from plugin when setting names, passing an empty destination name.

Test signals: `driver_test.go` covers capabilities, RPC sequence, gateway allocation check, endpoint/join data application, discovery, plugin errors, missing values, and rollback on interface application failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver_test.go

Purpose: Tests remote network driver plugin integration using HTTP test servers and temporary plugin specs.

Important APIs and functions: `handle` registers plugin RPC handlers. `setupPlugin` creates a plugin spec and activation endpoint. `testEndpoint` implements `InterfaceInfo`/`JoinInfo` assertions. Capability tests cover empty, extra, and invalid capabilities. `TestRemoteDriver` exercises capability negotiation, `GwAllocCheck`, network create/delete, endpoint create/delete, join/leave, operational info, and discovery. `TestDriverError` checks plugin `Err` propagation. `TestMissingValues` allows empty interface response fields. `TestRollback` verifies `DeleteEndpoint` is called when applying returned interface state fails.

Control flow: tests use real plugin HTTP client calls against `httptest.Server`, so they validate JSON encoding and plugin path construction.

State and persistence: writes temporary plugin spec files under the Docker plugin spec directory and cleans them up; plugin state is local test variables.

Dependencies and integration points: exercises `remote/driver.go`, plugin discovery, API wire structs, errdefs-compatible endpoint behavior, and route/gateway parsing.

Risks: uses global plugin spec path, so isolation depends on cleanup and permissions. External connectivity behavior is not deeply covered.

Test signals: strong regression coverage for remote plugin RPC adapter behavior and rollback paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/remote/driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/labels.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/labels.go

Purpose: Defines Windows driver label constants used to pass HNS/network/endpoint configuration through generic Docker network options.

Important APIs and constants: labels include network name, HNS ID, HNS ownership, routing domain, interface, QoS policies, VLAN, VSID, DNS suffix/servers, MAC pool/source MAC, ICC/DNS/gateway DNS controls, outbound NAT enablement, and outbound NAT exceptions.

Control flow: declarative constants only.

State and persistence: no state. Labels become part of network option maps and may be persisted by higher-level network config/state code.

Dependencies and integration points: consumed by Windows local drivers and Windows overlay code when parsing `netlabel.GenericData`.

Risks: label strings are user/plugin compatibility surface; renaming breaks existing network configs.

Test signals: no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/joinleave_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/joinleave_windows.go

Purpose: Implements Windows overlay join and NetworkDB peer event handling using HNS-backed endpoints and the shared overlay peer record schema.

Important APIs and functions: `Join` validates ids, finds network/endpoint, marshals a shared `overlay.PeerRecord` with endpoint IP/MAC and provider address, publishes it via `JoinInfo.AddTableEntry`, and disables gateway service when endpoint state requests it. `EventNotify` filters non-overlay peer table events, ignores local peers, decodes previous/new peer records, and calls Windows `peerDelete`/`peerAdd`. `DecodeTableEntry` returns nil data on Windows. `Leave` only validates ids.

Control flow: event handling mirrors Linux differential peer update logic but delegates to Windows HNS peer functions.

State and persistence: no datastore here. Mutates NetworkDB table entries through join info and HNS peer state through peer add/delete in another file.

Dependencies and integration points: integrates Windows overlay with shared Linux overlay protobuf/API package, libnetwork table watcher, and HNS peer database.

Risks: `Leave` does not remove local peer state directly; cleanup relies on endpoint/network lifecycle and NetworkDB. `DecodeTableEntry` is unimplemented, so diagnostics are weaker than Linux.

Test signals: no direct Windows overlay tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/joinleave_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_endpoint_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_endpoint_windows.go

Purpose: Implements Windows overlay endpoint create/delete and operational info through HNS endpoint APIs and Windows port allocation/policy helpers.

Important APIs and types: `endpoint` stores id, network id, HNS profile id, remote flag, MAC, IP, gateway-disable flag, and port mappings. State helpers manage the network endpoint map and stale endpoint removal. `CreateEndpoint` validates ids, deletes stale same-id HNS endpoint, validates IP/subnet, parses DNS and endpoint connectivity options, allocates host ports, constructs an `hcsshim.HNSEndpoint` with PA, outbound NAT, and port-binding policies, posts it to HNS, records profile/MAC/port policy state, and adds runtime endpoint. `DeleteEndpoint` releases ports, removes runtime endpoint, and deletes HNS endpoint. `EndpointOperInfo` returns HNS id, DNS flag, and copied port mappings.

Control flow: port allocation is rolled back via defer if creation fails before success. If HNS returns a generated MAC, it is propagated to `InterfaceInfo`. On policy parse failure after HNS create, the HNS endpoint is deleted.

State and persistence: runtime endpoint map, Windows port allocator state, and HNS endpoint state. No libnetwork datastore in this file.

Dependencies and integration points: depends on `hcsshim`, Windows driver DNS/port helpers, libnetwork endpoint options, and HNS policies.

Risks: HNS operations are external side effects and can partially fail. Endpoint deletion returns errors for missing endpoint instead of treating it as idempotent. Gateway is always disabled after endpoint creation.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_endpoint_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_network_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_network_windows.go

Purpose: Implements Windows overlay network create/delete, runtime state, HNS network creation, subnet lookup helpers, and stale VNI network cleanup.

Important APIs and types: `network` stores id, name, HNS ID, provider address, adapter, endpoints, subnets, secure flag, and a port allocator. `subnet` stores VNI, subnet IP, and gateway IP. `CreateNetwork` validates network info and IPv4 IPAM, deletes preexisting same-id network, parses generic labels including network name/interface/HNS ID/VNI list, requires VNIs for all subnets, removes stale networks that reuse a VNI, registers the peer table, adds runtime state, creates the HNS network, and writes the HNS ID back to generic data. `DeleteNetwork` deletes HNS network and runtime state. Helpers add/delete/lookup networks, convert HNS endpoints, create HNS network with VSID policies, and find subnets.

Control flow: VNI conflicts with existing runtime networks are resolved by deleting stale networks before creating the new HNS network. HNS network creation serializes subnets with VSID policies and records returned HNS ID/provider management IP.

State and persistence: runtime driver network table, HNS network state, and mutation of the generic data map with HNS ID. No explicit datastore here.

Dependencies and integration points: integrates with Windows HNS via `hcsshim`, shared overlay VNI label, libnetwork peer table registration, and Windows port allocator for endpoints.

Risks: create mutates caller-provided generic data. Stale-network deletion can remove existing runtime networks sharing a VNI. IPv6 IPAM is not used. Host mode globals are defined but not used in this file.

Test signals: no direct Windows overlay tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_network_windows.go -->
