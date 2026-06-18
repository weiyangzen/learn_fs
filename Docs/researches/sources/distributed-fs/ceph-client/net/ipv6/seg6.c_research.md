# sources/distributed-fs/ceph-client/net/ipv6/seg6.c

## Purpose

`seg6.c` is the core SRv6 control module. It validates SRH layout, extracts SRHs from packets, handles ICMP-invoking packet SRH metadata, exposes generic netlink commands for SRv6 HMAC keys and tunnel source address, initializes per-net SRv6 data, and registers the SRv6 tunnel/local subsystems.

## Important APIs, Types, And Functions

Exported helpers include `seg6_validate_srh()`, `seg6_get_srh()`, `seg6_icmp_srh()`, `seg6_init()`, and `seg6_exit()`. Per-net state is `struct seg6_pernet_data`, reached through `seg6_pernet(net)`, and contains a mutex, RCU-protected `tun_src`, and HMAC rhashtable when HMAC is configured.

Generic netlink handlers are `seg6_genl_sethmac()`, `seg6_genl_dumphmac_start()`, `seg6_genl_dumphmac()`, `seg6_genl_dumphmac_done()`, `seg6_genl_set_tunsrc()`, and `seg6_genl_get_tunsrc()`. They are registered under `seg6_genl_family` with admin permission flags for mutating/dumping protected state.

## Control Flow

`seg6_validate_srh()` verifies SRH type 4, exact encoded length, `segments_left` versus `first_segment` rules, and TLV bounds. For reduced SRH validation it permits `segments_left` to be at most `first_segment + 1`; otherwise it requires `segments_left <= first_segment`. It then walks trailing TLVs, ensuring every TLV header and declared length fits inside the SRH.

`seg6_get_srh()` uses `ipv6_find_hdr()` to locate a routing header, pulls enough skb data for the fixed and full SRH, reloads pointers after pull, and returns only a valid reduced-form SRH. `seg6_icmp_srh()` temporarily points the skb network header at the invoking packet inside an ICMP payload, calls `seg6_get_srh()`, records `IP6SKB_SEG6` and `srhoff` when found, then restores the original network header.

For HMAC configuration, `seg6_genl_sethmac()` validates key ID, secret length, algorithm, and optional secret. A zero secret length deletes a key; nonzero length replaces any existing key under the per-net mutex and inserts a prepared `seg6_hmac_info`. Dumping walks the per-net rhashtable with `rhashtable_walk_*`. Tunnel source updates allocate a new `in6_addr`, publish it with RCU, synchronize, then free the old pointer.

`seg6_init()` registers per-net state, generic netlink, SRv6 iptunnel ops, and SRv6 local behavior in order; failure unwinds in reverse. `seg6_exit()` unregisters local behavior, iptunnel ops, genl family, and per-net state.

## State And Persistence Behavior

State is per network namespace and allocated in `seg6_net_init()`. `tun_src` is RCU-protected and defaults to the all-zero address. HMAC information is stored in the per-net rhashtable initialized by `seg6_hmac_net_init()`. Generic netlink changes persist until key deletion, namespace teardown, or module cleanup. Per-net teardown frees HMAC state, tunnel source, and the container.

## Dependencies And Integration Points

The file depends on IPv6 packet parsing, generic netlink, `net/seg6.h`, `linux/seg6_genl.h`, optional `net/seg6_hmac.h`, and initialization hooks from `seg6_iptunnel` and `seg6_local`. The tunnel source is consumed by SRv6 iptunnel code when routes do not specify a per-route source.

## Risks And Edge Cases

SRH validation is security-critical because packet parsers and tunnel code rely on computed offsets. Incorrect reduced-header handling could accept impossible `segments_left` values or overrun TLVs. Generic netlink HMAC dumping exposes configured secrets to admin users, which is expected here but sensitive. `seg6_genl_get_tunsrc()` assumes `tun_src` exists after per-net initialization; per-net lifecycle ordering must preserve that invariant. HMAC code is compiled out cleanly by returning `-ENOTSUPP`, so callers must tolerate that.

## Test Signals

Good tests include SRH parser fuzzing, valid/reduced SRH extraction from nonlinear skbs, ICMP error metadata propagation, generic netlink set/get tunnel source, HMAC add/delete/dump with invalid lengths and algorithms, namespace create/destroy leak checks, and init unwind tests with fault injection in each registration step.
