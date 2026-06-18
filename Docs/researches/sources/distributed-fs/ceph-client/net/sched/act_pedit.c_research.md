# sources/distributed-fs/ceph-client/net/sched/act_pedit.c

## Purpose

`act_pedit.c` is the generic packet editor tc action. It applies one or more 32-bit masked writes or additions at fixed or computed offsets in Ethernet, network, IPv4, IPv6, TCP, or UDP headers.

## Important APIs, types, and functions

`tcf_pedit_init()` parses legacy and extended `TCA_PEDIT_*` attributes, validates key counts and offsets, copies `tc_pedit_key` arrays, parses optional extended key metadata with `tcf_pedit_keys_ex_parse()`, and RCU-installs `tcf_pedit_parms`. `tcf_pedit_act()` applies edits. `pedit_skb_hdr_offset()` and `pedit_l4_skb_offset()` locate selected headers, using `ipv6_find_hdr()` for IPv6 L4 offsets. `offset_valid()` bounds positive offsets against skb length and negative offsets against headroom. `tcf_pedit_offload_act_setup()` converts keys to `FLOW_ACTION_MANGLE` or `FLOW_ACTION_ADD`.

## Control flow

At init, every key is checked for 32-bit alignment unless it has an `offmask`; shifts are clamped; and a maximum offset hint is computed to preflight writability. Runtime ensures the relevant skb region is writable, then for each key resolves the base header, optionally reads an `at` byte to adjust the offset, validates bounds and alignment, reads a 32-bit word through `skb_header_pointer()`, computes either a SET or ADD value, applies the mask expression, and writes back with `skb_store_bits()` when using a scratch buffer.

## State and persistence

Persistent action state is an RCU parameter block with flags, key count, offset hint, key arrays, optional extended key array, and control action. Old parameter blocks are freed by `tcf_pedit_cleanup_rcu()`. Stats use the tc common action counters; bad edits increment overlimit qstats but return the configured action.

## Dependencies and integration points

It integrates with tc action IDR, classifier control actions, IPv4/IPv6 header parsing, skb non-linear access helpers, and flow offload. Extended keys are part of the tc UAPI for hardware-aware pedit actions.

## Risks and edge cases

Computed offsets, negative offsets into headroom, IPv6 extension-header traversal, non-linear skb writes, and mixed command offload validation are the main risks. The action does not recalculate protocol checksums after arbitrary edits; users must combine it with checksum-aware actions or edit fields where checksums are irrelevant.

## Test signals

Exercise legacy and extended keys, SET and ADD commands, Ethernet/network/TCP/UDP header bases, IPv6 extension headers, offmask/at computed offsets, invalid alignment, non-linear skbs, dump round trips, and offload rejection for mixed commands.
