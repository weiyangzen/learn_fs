# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_tc.c

## Purpose
`vcap_tc.c` implements reusable helpers that translate Linux TC flower dissector matches into Microchip VCAP rule keys. The functions inspect `struct flow_rule` match keys, convert masks and values into VCAP key formats, add those keys to `struct vcap_rule`, and report parse errors through TC extack.

## Important APIs, Types, and Functions
- State input is `struct vcap_tc_flower_parse_usage`, declared in `vcap_tc.h`.
- Exported GPL helpers translate Ethernet addresses, IPv4/IPv6 addresses, L4 ports, customer VLANs, generic VLANs, TCP flags, ARP fields, and IP TOS.
- Uses flow dissector match helpers such as `flow_rule_match_eth_addrs`, `flow_rule_match_ipv4_addrs`, `flow_rule_match_vlan`, `flow_rule_match_tcp`, and `flow_rule_match_arp`.
- Uses VCAP client APIs including `vcap_rule_add_key_u32`, `vcap_rule_add_key_u48`, `vcap_rule_add_key_u128`, `vcap_rule_add_key_bit`, and `vcap_netbytes_copy`.

## Control Flow
Each helper extracts the relevant flower match, skips fields whose mask is zero, adds one or more VCAP keys, sets the corresponding bit in `st->used_keys`, and returns 0. On the first `vcap_rule_add_key_*()` failure, the helper jumps to an `out` label, writes a category-specific `NL_SET_ERR_MSG_MOD()` message, and returns the error. ARP has extra validation that rejects masked sender/target hardware addresses because the IS2 ARP keyset does not support them.

## State and Persistence
The file does not persist state. It mutates only the caller-owned parse state and rule under construction: `st->vrule`, `st->used_keys`, and for VLAN parsing `st->tpid`. Byte order is normalized with `be16_to_cpu()` and `be32_to_cpu()` before adding integer VCAP keys.

## Dependencies and Integration Points
- Depends on kernel TC flower flow offload interfaces in `net/flow_offload.h`.
- Uses IPv6 helpers from `net/ipv6.h`, TCP flag constants from `net/tcp.h`, and Ethernet constants/address helpers.
- Integrates with Microchip VCAP client API through `vcap_api_client.h`.
- Exported symbols allow individual Microchip switch/NIC drivers to share the same TC flower parse helpers.

## Risks and Edge Cases
- `used_keys` is set even when an L3 protocol mismatch causes IPv4 or IPv6 fields to be ignored; callers must ensure this matches their unsupported-key accounting.
- ARP opcode mapping treats all non-request operations as reply after checking only that `mt.mask->op` is set; unsupported ARP op values may collapse into reply semantics.
- CVLAN TPID selection changes between `VID0/PCP0` and `VID1/PCP1`; incorrect TPID assumptions can place keys in the wrong VCAP fields.
- TCP flags are represented as individual ternary bits only when the corresponding mask bit is set.

## Test Signals
- TC flower offload tests should cover MAC, IPv4, IPv6, VLAN/CVLAN, TCP flags, ARP, and IP TOS translation.
- Negative tests should include unsupported ARP hardware address masks, VCAP key-add failures, and protocol mismatches.
- KUnit or driver tests can assert that `used_keys` and `tpid` are updated exactly as expected.
