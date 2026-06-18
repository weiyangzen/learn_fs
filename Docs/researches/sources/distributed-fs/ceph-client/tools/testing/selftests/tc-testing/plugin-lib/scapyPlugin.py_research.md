# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/scapyPlugin.py

## Purpose
Adds packet injection support to tc-testing cases using scapy. It sends packets after the command under test so tc filters/actions can update counters before verification.

## Important APIs, Types, And Functions
Class `SubPlugin(TdcPlugin)` overrides `post_execute()`. It imports `scapy.all`, reads each case's `scapy` block, requires `iface`, `count`, and `packet`, substitutes interface names from `NAMES`, evaluates the packet expression, and calls `sendp()`.

## Control Flow
If a case has no `scapy` key, the hook returns. A single scapy object is normalized into a list, allowing multiple packet sends. For each block the plugin validates keys, builds the packet with `eval()`, substitutes `$DEV*` interface placeholders, and sends the packet `count` times.

## State And Persistence
No persistent state other than mutated `scapyinfo['iface']` after substitution. Packet effects persist in network namespace counters and conntrack tables until teardown.

## Dependencies And Integration Points
Depends on the `scapy` Python package, raw packet privileges, and usually `nsPlugin`-created veth devices. Used by scapy examples and ct DNAT conflict tests.

## Risks
`eval()` on JSON-provided packet strings is powerful and requires trusted test files. Missing scapy exits the process at import time. Key validation reports missing keys but does not explicitly skip sending for malformed entries, so later errors can still occur.

## Test Signals
Packets appear on the requested interface, tc stats or conntrack state changes after `post_execute()`, and scapy import failures are clear.
