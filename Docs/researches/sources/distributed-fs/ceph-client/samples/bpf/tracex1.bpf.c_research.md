<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex1.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex1.bpf.c

## Purpose
`tracex1.bpf.c` is a kprobe sample that observes loopback packets entering `__netif_receive_skb_core*` and prints skb pointer and length.

## Important APIs, Types, And Functions
The single program `bpf_prog1()` attaches to `kprobe.multi/__netif_receive_skb_core*`. It uses `PT_REGS_PARM1()`, `BPF_CORE_READ()`, `BPF_CORE_READ_STR_INTO()`, `IFNAMSIZ`, and `bpf_trace_printk()`.

## Control Flow
On each kprobe hit, the program reads the `sk_buff *`, follows `skb->dev`, reads `skb->len` and device name, and prints only when the device name starts with `lo`.

## State And Persistence
There are no maps. The only output is transient trace pipe text.

## Dependencies And Integration Points
It depends on kprobe/multi attach support, BTF CO-RE field reads, and the networking receive path symbol naming. The userspace companion triggers loopback pings and reads trace output.

## Risks And Edge Cases
Kprobes are not stable ABI, and the wildcard is used to tolerate symbol suffix changes. CO-RE field reads depend on BTF availability. Trace printing is for debugging only.

## Test Signals
Running the companion should show trace lines like `skb <ptr> len <n>` during localhost ping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex1.bpf.c -->
