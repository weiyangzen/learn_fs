# sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.bpf.c

Purpose: lightweight tunnel BPF program that records packet length distribution.

Important APIs/types/functions: BPF array/hash map for histogram counts, `log2`, `log2l`, and `SEC("len_hist") int do_len_hist(struct __sk_buff *skb)`.

Control flow: handler reads `skb->len`, converts it to a log2 bucket, looks up the bucket count, increments it, and returns a pass verdict.

State and persistence: histogram counts are stored in a BPF map while the program is attached to a route/lwt hook.

Dependencies and integration: used by `lwt_len_hist_user.c` and `lwt_len_hist.sh`; requires BPF LWT support and `vmlinux.h` for CO-RE-style compilation.

Risks: bucket granularity is coarse by design. Attachment through `ip route encap bpf` is environment-dependent.

Test signals: attach via the script, send traffic over the route, and read nonzero histogram buckets.
