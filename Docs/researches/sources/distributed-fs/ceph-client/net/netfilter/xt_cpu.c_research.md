<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cpu.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_cpu.c

## Purpose
`xt_cpu.c` provides the `cpu` match, letting rules match the CPU currently processing the packet. It is intended for steering traffic across workers when RPS, IRQ affinity, or multiqueue NIC layouts make CPU selection meaningful.

## Important APIs, Types, and Functions
`cpu_mt()` compares `struct xt_cpu_info.cpu` with `smp_processor_id()`. `cpu_mt_check()` rejects unknown invert bits. `cpu_mt_reg` registers an NFPROTO_UNSPEC revision 0 match.

## Control Flow, State, and Persistence
There is no persistent state. Rule insertion validates `invert` as a single-bit boolean. Packet evaluation returns `(info->cpu == smp_processor_id()) ^ info->invert`.

## Dependencies and Integration Points
The module depends only on x_tables and per-CPU execution context. It can be used for IPv4 and IPv6 because registration is protocol-unspecified.

## Risks and Test Signals
Risks are operational rather than structural: CPU affinity can change with RPS, NAPI migration, softirq scheduling, or virtualization, so rule behavior may not map directly to ingress queue identity. Tests should pin traffic to known CPUs, validate inversion, reject malformed invert flags, and exercise IPv4 and IPv6 rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_cpu.c -->
