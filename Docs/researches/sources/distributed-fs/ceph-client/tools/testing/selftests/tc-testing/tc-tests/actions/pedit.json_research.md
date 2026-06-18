# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/pedit.json

## Purpose

`pedit.json` is a large parser and rendering suite for the `pedit` action, with 69 test cases. It validates raw offset edits, layered protocol edits, masks, retain/clear/invert/preserve/add/set operations, IPv4, IPv6, Ethernet, TCP, UDP, mixed edit sequences, control actions, and rejection paths.

## Important APIs, Types, and Schema

The file uses tc-testing manifest objects with `nsPlugin`, setup flushes, command under test, expected exit status, verification command, regex pattern/count, and teardown. The tc API is `$TC actions add|replace|ls|list action pedit`; many verification commands pipe to `grep 'key '` to focus on generated pedit keys.

The command grammar under test has two major forms. Raw operations use `munge offset <n> u8|u16|u32` plus `set`, `add`, `clear`, `invert`, `preserve`, `retain`, and dynamic `at <off> <offmask> <shift>`. Layered operations use `ex munge eth|ip|ip6|tcp|udp <field> <operation>`. The assertions inspect rendered key offsets, values, and masks.

## Control Flow

Each case generally starts from an empty `pedit` table. A command builds one or more pedit keys. Verification lists the action and matches the expected normalized key sequence. Invalid cases usually use `/bin/true` as `verifyCmd` with zero expected matches, meaning the primary signal is the command exit code. The invalid goto-chain replace case pre-populates index 90 and verifies the existing action remains after rejected replacement.

## State and Persistence Behavior

The key persistent state is the pedit action entry, including number of keys, action control, index, cookie, and ordered key list. Tests rely on ordering of emitted keys for multi-key operations. Negative raw offsets and mixed raw/layered cases show that pedit stores offsets relative to different protocol bases and can create several keys from one logical field, such as MAC or IPv6 addresses.

## Dependencies and Integration Points

The tests require `nsPlugin` and `$TC` with pedit support. They integrate with iproute2's pedit parser and pretty-printer rather than packet transmission. Layered `ex` operations depend on protocol header knowledge in iproute2 and kernel pedit support for extended keys.

## Risks

This file is highly sensitive to rendered key formatting, endian presentation, and mask normalization. Many regexes assume exact key order, spacing, and base names such as `ipv4+`, `ipv6+`, `eth+`, `tcp+`, and `udp+`. Invalid tests that verify with `/bin/true` do not independently query the action table, so they rely entirely on exit code and teardown. Mixed protocol edits do not prove packet correctness, only that keys are accepted and rendered.

## Test Signals

Coverage is deep. Raw tests cover aligned and misaligned offsets, u8/u16/u32 packing, overflow offsets, retain masks, clear/invert/preserve semantics, negative offsets, and dynamic offset metadata. Ethernet tests cover source, destination, type, add, invert, and invalid MAC/type values. IPv4 tests cover src/dst, ihl, dsfield, ttl, protocol, flags/fragment fields, tos/precedence operations, duplicate fields, transport-port aliases, and invalid TTL or missing extended mode. IPv6 tests cover src/dst expansion, traffic class, flow label, payload length, next header, hop limit, and invalid retain. TCP/UDP tests cover ports and flags. The final mixed cases ensure raw and layered edits can coexist in one action.
