# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/csum.json

## Purpose
Defines 23 tc tests for the `csum` action, including checksum target parsing, combined protocols, batching, cookies, invalid controls, and `no_percpu`.

## Important APIs, Types, And Functions
Tests cover aliases `iph`, `ip4h`, `ipv4h`, protocols `icmp`, `igmp`, `tcp`, `udp`, `udplite`, `sctp`, invalid `foobar`, invalid `udp xor iph`, combinations with `and/or`, all seven checksum targets, cookies, batches of 32 add/delete actions, invalid `goto chain`, and `no_percpu`.

## Control Flow
Cases run inside `nsPlugin`, create actions with `tc actions add/replace/del`, verify `tc actions get/list` output against regexes, and use setup/teardown to isolate the action table. Batch cases synthesize many `action csum ... index $i` clauses in a shell loop.

## State And Persistence
Per-namespace tc action state persists for the case duration. Batch tests create up to 32 indexed actions and remove them in paired delete cases or teardown.

## Dependencies And Integration Points
Depends on `NET_ACT_CSUM`, namespace support, and tc parser support for protocol aliases and `no_percpu`.

## Risks
Protocol order in `tc` output is normalized and regexes assume that order. Batch shell quoting is brittle. Negative cases depend on parser rejecting malformed combinations without leaving partial state.

## Test Signals
Signals are correct normalized protocol lists, control action display, cookie display, exact batch ref-count totals, deletion clearing actions, and rejected invalid target/control cases.
