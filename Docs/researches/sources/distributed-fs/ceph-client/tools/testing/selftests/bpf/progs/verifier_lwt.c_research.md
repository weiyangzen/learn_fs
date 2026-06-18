# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_lwt.c

## Purpose
This file validates verifier context and direct packet access rules for Lightweight Tunnel BPF program types (`lwt_in`, `lwt_out`, and `lwt_xmit`).

## Important APIs, Types, And Functions
It uses `struct __sk_buff` fields `data`, `data_end`, and `tc_classid`, packet direct access, and the helper `bpf_skb_change_head` in the headroom test. Sections cover LWT input, output, transmit, and socket aliases used to exercise invalid context accesses.

## Control Flow
The first tests attempt direct packet writes and show that LWT_IN/LWT_OUT reject writes while LWT_XMIT permits them after bounds checks. Read tests verify packet reads are accepted. Later tests validate overlapping packet bounds checks, headroom adjustment invalidating/revalidating packet pointers, and rejection of `tc_classid` access.

## State And Persistence
No persistent state is kept. Verifier state consists of packet pointer ranges, context field permissions, packet-write capability per program type, and pointer invalidation after helper calls.

## Dependencies And Integration Points
It depends on the BPF selftest harness, `__sk_buff` layout offsets, and verifier program-type access tables for LWT.

## Risks
If packet writes are enabled for the wrong LWT direction, programs could mutate packets where the kernel expects read-only access. Incorrect context permissions could expose unsupported `__sk_buff` fields.

## Test Signals
Expected messages include `cannot write into packet` and `invalid bpf_context access`, while valid read/write cases assert `__retval(0)`.
