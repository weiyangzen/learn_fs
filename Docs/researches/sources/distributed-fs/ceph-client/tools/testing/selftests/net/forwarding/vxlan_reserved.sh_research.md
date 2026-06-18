# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/vxlan_reserved.sh

## Purpose

This selftest verifies how a VXLAN device handles reserved bits in the VXLAN header. It crafts VXLAN UDP packets with clean and intentionally modified reserved bits, then checks whether packets are accepted or counted as VXLAN RX errors according to the device `reserved_bits` mask.

## Important APIs, Types, and Functions

The script uses `lib.sh`, `adf_` helpers, `tc`, `$MZ`, bridge/VXLAN commands, and link statistics. Important functions are `vxlan_header_bytes`, `neg_bytes`, `vxlan_ping_do`, `vxlan_device_add`, `vxlan_all_reserved_bits`, `vxlan_ping_vanilla`, `vxlan_ping_reserved`, `vxlan_ping_test`, `__default_test_do`, `default_test`, `plain_test`, and `reserved_test`.

## Control Flow

Setup creates a host, switch bridge, routed peer, and a VXLAN bridge port. Each test creates `vx1` with a particular `reserved_bits` attribute, sends 10 clean decapsulated ICMP packets and one packet for every reserved header bit, then compares ingress ICMP captures on the host and VXLAN RX error deltas. `in_defer_scope` ensures test-specific VXLAN devices and filters are removed.

## State and Persistence Behavior

Temporary state includes a bridge, VXLAN device, host ingress drop/counter filter, FDB/bridge membership, underlay routes, and crafted packets. No persistent storage is used.

## Dependencies and Integration Points

The test depends on `mausezahn` for byte-level packet crafting, `tc` ingress counters, bridge/VXLAN support, and link RX error statistics. It integrates directly with the kernel VXLAN parser and `reserved_bits` netlink attribute behavior.

## Risks and Edge Cases

The bit numbering is manually encoded into an 8-byte VXLAN header, with bit 4 always treated as the I flag and bits 32-55 as VNI. A mismatch between test bit numbering and kernel semantics would invalidate expectations. The default case expects all 39 non-I/non-VNI bits to be rejected, while selected masks allow exactly one reserved bit.

## Test Signals

Passing signals are 10 accepted clean packets, expected accepted reserved-bit packet counts of 0 or 1 depending on mask, and RX error deltas equal to rejected packet counts for default, plain mask, and selected bit masks 0, 10, 31, 56, and 63.
