# sources/distributed-fs/ceph-client/net/core/hotdata.c

Purpose: Defines cacheline-aligned global networking hot data defaults and the aligned data object used by other net/core paths.

Important APIs, types, and functions: Exports `struct net_hotdata net_hotdata`, initialized with the global offload list head and defaults for GRO normal batching, netdev budget, budget usecs, timestamp prequeue, backlog limit, qdisc burst, TX/RX weights, max skb frags, deferred skb free cap, and per-cpu memory reserve. Also defines `struct net_aligned_data net_aligned_data`.

Control flow: There is no executable control flow beyond static initialization and export. Other networking paths mutate or read fields directly or via sysctl-facing code.

State and persistence: This is runtime global kernel state. Defaults persist for the boot lifetime and may be adjusted by sysctl or subsystem initialization depending on field. No disk persistence is implemented here.

Dependencies and integration points: `gro.c` and `gso.c` use `offload_base`; `gro_cells.c` uses `max_backlog`; netdev budget and weights feed core receive/transmit scheduling; memory reserve and skb frag defaults integrate with socket memory and skb allocation policy.

Risks: Because fields are hot and global, layout/cacheline changes can affect performance. Unsafe updates to list or tunables without expected synchronization can race readers. Changing defaults alters system-wide networking behavior.

Test signals: Boot-time sanity should confirm offload list initialization before protocol registration, sysctl reads/writes for tunables, receive backlog behavior at default `max_backlog`, and performance regressions around hot cacheline fields.
