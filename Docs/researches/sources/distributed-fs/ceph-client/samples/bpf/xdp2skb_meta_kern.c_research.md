<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta_kern.c

## Purpose
`xdp2skb_meta_kern.c` demonstrates passing metadata from an XDP program to a tc ingress program using `xdp_md->data_meta`, then copying that value to `skb->mark`.

## Important APIs, Types, And Functions
`struct meta_info` contains a 32-bit mark. Programs are `_xdp_mark()` in section `xdp_mark` and `_tc_mark()` in section `tc_mark`. It uses `bpf_xdp_adjust_meta()` and writable `ctx->mark` on `struct __sk_buff`.

## Control Flow
The XDP program reserves metadata space before packet data, reloads invalidated packet pointers, bounds-checks the metadata area, writes mark `42`, and passes the packet. The tc program checks whether metadata exists; if not, it sets mark `41`, otherwise it copies `meta->mark` to `skb->mark`.

## State And Persistence
There are no maps. Metadata exists only while the packet moves from XDP to skb/tc processing; mark persists on the skb after tc.

## Dependencies And Integration Points
It depends on driver support for XDP metadata, XDP_PASS handoff to skb, tc ingress attachment, and the shell wrapper that loads both sections.

## Risks And Edge Cases
Helpers that change packet data invalidate pointers, so the program reloads `ctx->data` after adjustment. Drivers lacking metadata support return an error and the sample returns `XDP_ABORTED`. Metadata layout is private to these two programs.

## Test Signals
Packets traversing both hooks should have skb mark `42`; packets without metadata should receive mark `41`. XDP exception tracepoints can reveal `XDP_ABORTED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp2skb_meta_kern.c -->
