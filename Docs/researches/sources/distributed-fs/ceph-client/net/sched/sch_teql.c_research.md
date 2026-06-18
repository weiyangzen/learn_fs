# sources/distributed-fs/ceph-client/net/sched/sch_teql.c

Purpose: implements TEQL, a virtual link equalizer. Module load creates `teqlN` master netdevices and matching qdisc ids; attaching the qdisc as root to slave devices lets the master transmit by rotating across active slaves.

Important APIs/types/functions: `struct teql_master` embeds dynamic `Qdisc_ops`, the master netdevice, circular slave qdisc list, module list link, and TX stats. `struct teql_sched_data` stores next slave, master pointer, and a per-slave skb queue. `teql_enqueue()` and `teql_dequeue()` manage slave queues. `teql_qdisc_init()` validates root-only attach and slave compatibility. `teql_master_xmit()` chooses a usable slave, resolves neighbor headers, locks the slave TX queue, calls `netdev_start_xmit()`, and updates stats. Init/exit allocate/register and unregister master devices and qdisc ops.

Control flow: after module init registers masters and qdiscs, each slave joins by installing the qdisc. The first slave seeds master MTU/flags; later slaves are inserted into a circular list. Master transmit loops from `master->slaves`, skips stopped/detached devices, performs neighbor resolution when needed, transmits on the first usable slave, and advances the rotation. If all are busy, the master queue is stopped; if none can resolve/transmit, the packet is dropped.

State and persistence: state is module/netdevice memory: master list, circular slave qdisc lists, per-slave skb queues, and TX counters. It persists only while the module/device instances exist. Removing the last slave resets the master queue.

Dependencies/integration: netdevice registration, qdisc registration, root qdisc API, neighbor cache, dst entries, L2 header creation, TX queue state/locking, module parameters, and ARP/header flags.

Risks: packet reordering is inherent and severe with mismatched link speeds. Only neighbor-cache protocols resolve through the equalizer. Circular slave unlinking is delicate. Master transmit mutates `skb->dev` and header layout during retries. MTU/header/flag compatibility can reject mixed devices at attach/open time.

Test signals: module load with multiple equalizers, root-only attach rejection, loop prevention, first/last slave attach/detach, master open without slaves, MTU/header compatibility, round-robin TX, busy queue stop/wake, neighbor resolution failure/retry, MTU change validation, and TX/error/drop stats.
