# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/police.json

## Purpose

`police.json` defines 34 tc-testing cases for the `police` action. It verifies rate and burst parsing, MTU and peakrate coupling, overhead and linklayer options, conform-exceed control pairs, standalone control actions, packets-per-second policing, cookies, maximum index, listing, getting, deleting, flushing, and skip hardware flags.

## Important APIs, Types, and Schema

The manifest uses the common tc-testing schema and requires `nsPlugin`. Commands exercise `$TC actions add|delete|flush|ls|list|get|show action police`. The police grammar under test includes `rate`, `burst`, `mtu`, `peakrate`, `overhead`, `linklayer`, `conform-exceed`, `pkts_rate`, `pkts_burst`, `index`, `cookie`, `skip_hw`, and controls such as `continue`, `drop`, `ok`, `reclassify`, and `pipe`.

## Control Flow

Cases flush police actions, optionally pre-create an entry, run the command under test, and verify with list/show/get. Regexes assert normalized rates, bursts, MTU, peakrate, overhead, linklayer, action controls, index values rendered in hexadecimal for police handles, cookies, and skip flags. Negative cases expect `255` and absence of the invalid rendering.

## State and Persistence Behavior

Police action state includes rate tables, burst/MTU, optional peakrate table, linklayer metadata, conform/exceed actions, packet-rate fields, cookie, and index. Duplicate-index and invalid replace tests intentionally preserve existing state. The maximum index test uses `4294967295`, rendered as `0xffffffff`.

## Dependencies and Integration Points

The file depends on kernel police action support and iproute2 unit parsing. It is action-table focused and does not attach filters or send traffic. It integrates with tc-testing regex matching and relies on unit normalization such as `1Kbit`, `10Kb`, `2Kb`, `1024Kb|1Mb`, and packet-rate fields.

## Risks

Unit rendering is the largest stability risk because iproute2 may normalize bits, bytes, and metric suffixes differently. Some patterns encode default MTU values (`2Kb` or very large packet MTU for pps mode) and default action `reclassify`, which can change across implementations. The tests validate parser state but not actual policing behavior under traffic load.

## Test Signals

The suite covers valid basic policing, duplicate index rejection, MTU, peakrate requiring MTU, overhead, Ethernet and ATM linklayers, conform-exceed pairs including numeric control IDs, invalid rate/burst/peakrate/MTU values, cookie, maximum index, delete, get single action, get without index rejection, list many actions, flush, individual control actions, invalid goto-chain controls, packet-per-second policing, rejection of combined bps and pps mode, and `skip_hw` rendering.
