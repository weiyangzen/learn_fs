# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_netbios_ns.c

## Purpose
This small helper tracks locally originating NetBIOS name service broadcast requests on UDP port 137. It uses the generic broadcast helper to create a short-lived expectation for replies from the destination network, allowing broadcast name service responses to be related to the originating conntrack.

## Important APIs, Types, And Functions
The module parameter is `timeout`, defaulting to 3 seconds. `exp_policy` allows one expected reply. `netbios_ns_help()` delegates all packet-specific behavior to `nf_conntrack_broadcast_help(skb, ct, ctinfo, timeout)`. The single registered `helper` is named `netbios-ns`, IPv4-only, UDP, source port 137, and uses `exp_policy`.

## Control Flow
On module init, `nf_conntrack_netbios_ns_init()` sets `exp_policy.timeout` from the module parameter and registers the helper. When a matching packet invokes the helper, the generic broadcast helper handles direction checks, expectation creation, and timeout behavior. Module exit unregisters the helper.

## State And Persistence
The only module state is the timeout parameter, expectation policy, and helper registration. Runtime state is in conntrack expectations and expires quickly. There is no persistent storage.

## Dependencies And Integration Points
The file depends on core conntrack, helper registration, expectations, and `nf_conntrack_broadcast_help()`. It is IPv4-specific and registers legacy/helper aliases for autoload.

## Risks
The helper trusts the generic broadcast helper for safety. The short timeout limits exposure, but overly broad broadcast expectations can still admit unexpected replies during the window. Timeout changes are read-only after module load because the parameter is mode `0400`.

## Test Signals
Tests should verify helper registration on UDP/IPv4 port 137, correct timeout propagation to `exp_policy`, expectation creation for local broadcast queries, expiry after the configured timeout, no IPv6 registration, unload cleanup, and behavior with timeout values at low/high extremes.
