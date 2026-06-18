# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/creating-testcases/scapy-example.json

## Purpose
Demonstrates tc-testing cases that use `nsPlugin` and `scapyPlugin` to send packets and verify tc statistics through JSON output.

## Important APIs, Types, And Functions
The cases use `plugins.requires`, setup commands for ingress qdisc management, `cmdUnderTest` adding a flower filter with `action ok`, a `scapy` block with `iface`, `count`, and packet expression, `verifyCmd` using `tc -s -j`, and `matchJSON` path/value assertions.

## Control Flow
Each case creates or resets ingress qdisc on `$DEV1`, installs a flower filter matching a source IP, sends packets from `$DEV0` through scapy after command execution, then verifies packet stats at a nested JSON path. The second case intentionally uses a packet count that does not match the expected value, demonstrating failure behavior.

## State And Persistence
Temporary state is a network namespace with veth devices and an ingress qdisc/filter, removed in teardown and namespace cleanup.

## Dependencies And Integration Points
Integrates with `nsPlugin.py` for namespace/device setup and `scapyPlugin.py` for packet injection. Requires tc flower classifier and action support.

## Risks
The `packet` field is evaluated by Python `eval()` in the scapy plugin, so these examples rely on trusted test data. JSON paths are brittle to tc output schema changes.

## Test Signals
Successful packet counter increments in `tc -s -j filter ls` for the matching packet case, and a deliberate mismatch in the wrong-count example.
