# sources/distributed-fs/ceph-client/net/ipv4/fou_bpf.c

## Purpose
`fou_bpf.c` exposes unstable TC-BPF kfunc helpers for configuring and reading FOU/GUE tunnel encapsulation metadata on sk_buffs that use collect-metadata IP tunnel devices.

## Important APIs, Types, And Functions
The local `struct bpf_fou_encap` carries UDP source and destination ports. `enum bpf_fou_encap_type` selects FOU or GUE. The kfuncs are `bpf_skb_set_fou_encap` and `bpf_skb_get_fou_encap`, registered through `register_fou_bpf` using a `btf_kfunc_id_set` for `BPF_PROG_TYPE_SCHED_CLS`.

## Control Flow
`bpf_skb_set_fou_encap` treats the BPF context as `struct sk_buff`, retrieves `skb_tunnel_info`, validates that metadata exists and is TX metadata, maps the requested type to `TUNNEL_ENCAP_FOU`, `TUNNEL_ENCAP_GUE`, or `TUNNEL_ENCAP_NONE`, mirrors checksum intent from `IP_TUNNEL_CSUM_BIT`, and stores UDP ports in `info->encap`. `bpf_skb_get_fou_encap` validates tunnel info and copies the stored ports back to BPF memory.

## State And Persistence
The file does not own persistent state. It mutates per-packet tunnel metadata inside `struct ip_tunnel_info`. Registration persists only as module-owned BTF kfunc metadata and depends on the FOU module lifetime.

## Dependencies And Integration Points
It depends on BPF kfunc/BTF infrastructure, `dst_metadata` tunnel metadata, `net/fou.h`, and the FOU core module that calls `register_fou_bpf` during initialization. It is intended for TC classifier programs after `bpf_skb_set_tunnel_key` has already populated IP tunnel key fields.

## Risks
This is explicitly unstable API surface. Main behavioral risks are accepting packets without TX tunnel metadata, stale encap flags if type is invalid, and verifier or BTF registration regressions. Since BPF programs supply `encap`, NULL checking is essential.

## Test Signals
Test with TC-BPF programs on collect-metadata IPIP tunnels that set FOU and GUE ports, verify generated tunnel packets, verify checksum flag propagation, reject missing tunnel metadata, reject NULL encap pointers, and ensure kfunc registration appears only for scheduler classifier programs.
