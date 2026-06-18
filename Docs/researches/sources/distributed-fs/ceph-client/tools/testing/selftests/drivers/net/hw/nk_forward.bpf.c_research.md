
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_forward.bpf.c`

## Purpose
Provides the tc ingress BPF forwarding program used by `NetDrvContEnv` and netkit queue lease tests. It redirects selected IPv6 traffic from the physical NIC ingress path to the netkit peer with `bpf_redirect_peer()`.

## Important APIs, Types, And Functions
- `SEC("tc/ingress") int tc_redirect_peer(struct __sk_buff *skb)` is the only program.
- Global `.bss` variables `netkit_ifindex` and `ipv6_prefix` are patched by userspace after load.
- `ctx_ptr()` safely casts packet offsets from `__sk_buff`.
- `v6_p64_equal()` compares the first 64 bits of destination IPv6 address with the configured prefix.

## Control Flow
The program exits with `TC_ACT_OK` for non-IPv6 packets, truncated Ethernet headers, truncated IPv6 headers, or IPv6 destinations outside the configured prefix. Matching IPv6 packets are redirected to `netkit_ifindex`.

## State And Persistence
State is only BPF global data in `.bss`, populated by `NetDrvContEnv._attach_bpf()` through `bpftool map update`. The program itself has no maps for counters or persistence beyond the globals.

## Dependencies And Integration Points
Built as `nk_forward.bpf.o` and attached by `tc filter add ... ingress bpf obj ... sec tc/ingress direct-action`. Depends on kernel helpers `bpf_redirect_peer()` and BPF CO-RE style global data availability.

## Risks
Only the upper 64 bits of IPv6 destination are compared, so the userspace prefix must be a /64 as assumed by `NetDrvContEnv`. The program does not inspect L4 protocol or route state, so any IPv6 packet to that prefix is forwarded.

## Test Signals
Validated indirectly by `nk_netns.py` and `nk_qlease.py`: pings or io_uring zero-copy receive traffic must reach the netkit namespace endpoint through the redirected path.
