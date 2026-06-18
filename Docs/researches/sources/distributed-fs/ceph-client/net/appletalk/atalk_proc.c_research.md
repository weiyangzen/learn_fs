# sources/distributed-fs/ceph-client/net/appletalk/atalk_proc.c

Purpose: provides `/proc/net/atalk/*` seq_file views for AppleTalk interfaces, routes, sockets, and AARP entries.

Important APIs, types, and functions: interface, route, and socket seq operation sets are `atalk_seq_interface_ops`, `atalk_seq_route_ops`, and `atalk_seq_socket_ops`. Public lifecycle functions are `atalk_proc_init` and `atalk_proc_exit`. It also references `aarp_seq_ops` for `/proc/net/atalk/arp`.

Control flow: init creates the `atalk` proc directory under `init_net.proc_net`, then creates `interface`, `route`, `socket`, and `arp` entries. Each seq iterator takes the matching global AppleTalk lock in `start`, walks a linked list or hlist in `next`, formats rows in `show`, and releases the lock in `stop`. Failure during creation removes the entire `atalk` subtree.

State and persistence: no independent protocol state; it reads DDP global lists (`atalk_interfaces`, `atalk_routes`, `atalk_sockets`, and `atrtr_default`) and AARP global tables. Proc entries exist only while the module is loaded and `CONFIG_PROC_FS` is enabled.

Dependencies and integration points: depends on procfs, seq_file, init_net proc namespace, DDP locks and structures, socket ownership helpers, and AARP iterator private state for the `arp` file.

Risks: output is init-net only. Route display emits the default route inside every non-header route row when `atrtr_default.dev` is set, which can duplicate default output during iteration. Long-held read locks while formatting can block writers for large tables.

Test signals: module init failure unwinding, reading all proc files while interfaces/routes/sockets/AARP entries change, namespace behavior, permission mode `0444`, and lockdep during concurrent ioctls and proc reads.
