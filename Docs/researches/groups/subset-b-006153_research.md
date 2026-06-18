# Research Report: subset-b-006153

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_fd.c -->
# sources/distributed-fs/ceph-client/net/9p/trans_fd.c

Purpose: implements the 9P `tcp`, `unix`, and explicit `fd` transports by wrapping sockets or user-provided file descriptors in an asynchronous mux. It is the generic stream/file backend for v9fs clients when virtio-like shared-memory transports are not used.

Important APIs, types, and functions: `struct p9_trans_fd` holds read/write `struct file` references and an embedded `struct p9_conn`. `struct p9_conn` owns sent and unsent request lists, current read/write request references, poll wait entries, and read/write work items. `p9_fd_create_tcp`, `p9_fd_create_unix`, and `p9_fd_create` connect the transport; `p9_fd_request`, `p9_fd_cancel`, `p9_fd_cancelled`, and `p9_fd_close` implement the `p9_trans_module` contract. `p9_read_work`, `p9_write_work`, `p9_poll_mux`, and `p9_poll_workfn` are the event engine.

Control flow: create opens a TCP/Unix socket or duplicates supplied fds, forces nonblocking I/O, marks the client connected, and registers poll wait hooks. Requests are queued on `unsent_req_list`; write work moves one request to `req_list`, writes its 9P frame incrementally, and keeps a reference until the frame is fully written. Read work first reads the 9P header into `tmp_buf`, resolves the tag with `p9_tag_lookup`, switches to the request response buffer, then completes the request through `p9_client_cb`.

State and persistence: all state is per client except the global poll pending list and reserved port sysctl-style globals. Request state transitions use `REQ_STATUS_UNSENT`, `SENT`, `RCVD`, `FLSHD`, and `ERROR`; `m->err` makes cancellation one-shot. State is volatile kernel memory; no persistence survives unmount/module removal.

Dependencies and integration points: depends on vfs `kernel_read`/`kernel_write`, socket creation/connect, poll wait queues, workqueues, and the net/9p client tag table. It registers three transports with `v9fs_register_trans` and reports mount options with `seq_file`.

Risks: the transport mutates file flags with intentional `data_race()` to force `O_NONBLOCK`; incorrect sharing of fds can break mounts. Header parsing, tag lookup, request list removal, and work cancellation are concurrency-sensitive. Unexpected tags or overlarge responses disconnect the whole client. The TCP privileged-port bind loop can fail under port exhaustion.

Test signals: useful checks include mounting over `trans=tcp`, `trans=unix`, and `trans=fd`; exercising short reads/writes and `EAGAIN`; flush/cancel races; server disconnects; malformed tags/lengths; module unload after active requests; and KCSAN/lockdep around request lists and poll wait removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_rdma.c -->
# sources/distributed-fs/ceph-client/net/9p/trans_rdma.c

Purpose: provides a 9P transport over reliable connected RDMA. It maps each request and expected reply into RDMA send/receive work requests and integrates with RDMA CM for address resolution, route resolution, and connection management.

Important APIs, types, and functions: `struct p9_trans_rdma` tracks RDMA CM state, CM ID, PD, QP, CQ, queue depths, semaphores, `excess_rc`, and connection completion. `struct p9_rdma_context` wraps an `ib_cqe`, DMA address, and either a request or receive fcall. Core functions are `p9_cm_event_handler`, `post_recv`, `rdma_request`, `recv_done`, `send_done`, `rdma_create_trans`, `rdma_close`, `rdma_cancelled`, and `p9_rdma_bind_privport`.

Control flow: creation allocates transport state, creates an RDMA CM ID, optionally binds a privileged local port, resolves IPv4 address and route, allocates CQ and PD, creates the QP, connects, then marks the client connected. Each request usually posts a receive buffer first, clears `req->rc.sdata` so ownership belongs to the receive context, maps and posts the send buffer, and marks the request sent before `ib_post_send` to avoid a fast-reply race. Completion callbacks unmap DMA, release queue semaphores, parse tags, attach response buffers, and call `p9_client_cb`.

State and persistence: state is in RDMA objects and per-client memory. `sq_sem` and `rq_sem` bound outstanding work. `excess_rc` records receive buffers that remain posted after a flush or a send-side failure, so later requests can skip posting another receive. No persistent on-disk state exists.

Dependencies and integration points: depends on `rdma_cm`, `ib_verbs`, `net/9p`, semaphores, completions, and socket address parsing. It registers `p9_rdma_trans`, advertises `pooled_rbuffers = true`, and does not support vmalloc request buffers because DMA mapping needs suitable memory.

Risks: receive-before-send is necessary but creates hard-to-test `excess_rc` paths. Error handling changes RDMA and client state to flushing/disconnected but does not cancel every outstanding request locally. CM event handler uses strict `BUG_ON` assumptions for event order. DMA mapping, buffer ownership, and duplicate reply detection are critical.

Test signals: RDMA mount/connect success, address/route/connection failure paths, queue-depth exhaustion, interruptible waits, flushes without replies, send errors after receive posting, duplicate or malformed replies, device removal events, and module unload should all be tested under RDMA-capable CI or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_usbg.c -->
# sources/distributed-fs/ceph-client/net/9p/trans_usbg.c

Purpose: implements a USB gadget function and matching 9P transport named `usbg`, allowing a USB peripheral to mount a host-exported 9P filesystem over two bulk endpoints.

Important APIs, types, and functions: `struct f_usb9pfs` combines the 9P client, endpoint pointers, USB requests, completions, buffer length, and `usb_function`. `struct f_usb9pfs_opts` and `struct f_usb9pfs_dev` provide configfs instance state, tag selection, and in-use tracking. Transport entry points are `p9_usbg_create`, `p9_usbg_request`, `p9_usbg_cancel`, and `p9_usbg_close`; USB lifecycle functions include `usb9pfs_alloc_instance`, `usb9pfs_alloc`, `usb9pfs_func_bind`, `usb9pfs_set_alt`, `usb9pfs_disable`, and `usb9pfs_func_unbind`.

Control flow: configfs creates a tagged function instance and binds it into a composite USB configuration. Binding allocates interface IDs and autoconfigures IN/OUT bulk endpoints; `set_alt` enables endpoints and allocates one IN and one OUT request. A 9P mount selects the instance by tag and marks it in use. A request waits for the previous receive completion, queues the 9P request on the IN endpoint, waits for transmit completion, and queues the OUT request for the reply. RX completion parses the header, looks up the tag, bounds-checks against the response buffer, copies the reply, and calls `p9_client_cb`.

State and persistence: state is held in global `usbg_instance_list`, per-instance tags, an `inuse` flag, one request per endpoint, and `send`/`received` completions. The only user-visible persistent-ish configuration is configfs state while the gadget exists; it is not durable across module removal.

Dependencies and integration points: depends on USB composite/configfs APIs, endpoint descriptors for full/high/super speed, `DECLARE_USB_FUNCTION`, and v9fs transport registration. The `buflen` configfs attribute controls transport `maxsize` but cannot be changed once functions are referenced.

Risks: the implementation serializes requests through single IN/OUT USB requests, so concurrency assumptions are narrow. Prefix matching in `p9_usbg_create` uses `strncmp(devname, tag, strlen(devname))`, making ambiguous tag prefixes a risk. Completion and close paths must handle in-flight requests without double completion or leaked references. Disconnects can leave the client temporarily disconnected until endpoints are re-enabled.

Test signals: create multiple configfs instances with distinct and prefix-overlapping tags, bind/unbind at all supported speeds, mount while endpoints are disabled/enabled, send malformed or overlarge replies, kill waits, unplug during TX/RX, change `buflen` before/after reference, and run lockdep around spinlock and configfs mutex interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_usbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_virtio.c -->
# sources/distributed-fs/ceph-client/net/9p/trans_virtio.c

Purpose: implements the default virtio 9P transport, discovering virtio 9P channels, matching mounts by mount tag, and sending 9P requests through a single virtqueue with optional zero-copy user data.

Important APIs, types, and functions: `struct virtio_chan` stores channel in-use state, virtqueue, client, tag, wait queue, scatterlist array, and zero-copy page limit. `p9_virtio_probe` and `p9_virtio_remove` handle virtio device lifecycle; `p9_virtio_create` and `p9_virtio_close` attach/detach mounts; `p9_virtio_request` sends normal requests; `p9_virtio_zc_request`, `p9_get_mapped_pages`, `pack_sg_list`, and `pack_sg_list_p` implement scatter-gather and zero-copy.

Control flow: probe requires the `VIRTIO_9P_MOUNT_TAG` feature, reads the tag from config space, creates a `mount_tag` sysfs attribute, initializes the channel wait queue and scatterlist, and adds the channel to a global list. Mount creation locks the list, finds an unused tag match, marks it in use, and attaches the client. Requests pack outgoing and incoming buffers into scatterlists, call `virtqueue_add_sgs`, wait and retry on `-ENOSPC`, and kick the queue. `req_done` drains completed buffers, sets response length, invokes `p9_client_cb`, and wakes waiters for ring space.

State and persistence: global state includes `virtio_chan_list`, `virtio_9p_lock`, and `vp_pinned`. Per-channel `ring_bufs_avail` gates waiters. Zero-copy pins pages up to `p9_max_pages`, then unpins and wakes global waiters after completion or failure. No state persists beyond the virtio device/module lifetime.

Dependencies and integration points: depends on virtio core, virtio 9P config, scatterlist, page pinning/iov iter helpers, sysfs, and net/9p. It registers both a `virtio_driver` and `p9_trans_module`; the mount tag sysfs file is intended for udev rules.

Risks: no request cancel is supported; cancelled zero-copy requests must drop references correctly. Page pin accounting is global and can become a denial-of-service boundary. `handle_rerror` copies error payload out of user pages into static response data and truncates long errors. Remove waits indefinitely for `inuse` to clear, only logging periodically.

Test signals: virtio probe without config access or mount-tag feature, duplicate tag mount attempts, virtqueue full retries, zero-copy read/write with user and kernel iovecs, interrupted waits, RERROR on zero-copy reads, page pin limit pressure, hot-remove while mounted, and sysfs `mount_tag` visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_xen.c -->
# sources/distributed-fs/ceph-client/net/9p/trans_xen.c

Purpose: implements the Xen frontend transport for 9P by negotiating Xenstore state with a backend and exchanging 9P frames over grant-table-backed flexible rings and event channels.

Important APIs, types, and functions: `struct xen_9pfs_front_priv` stores one share, its tag, Xenbus device, attached client, and ring array. `struct xen_9pfs_dataring` stores the shared data interface, grant refs, event channel/IRQ, ring buffers, wait queue, lock, and response work. Transport functions are `p9_xen_create`, `p9_xen_request`, `p9_xen_close`, and `p9_xen_cancel`. Frontend lifecycle is handled by `xen_9pfs_front_init`, `xen_9pfs_front_alloc_dataring`, `xen_9pfs_front_changed`, `xen_9pfs_front_remove`, and `xen_9pfs_front_free`.

Control flow: module init registers the 9P transport only in Xen domains and registers a Xenbus frontend. When the backend reaches `InitWait`, frontend init validates protocol version 1, allocates two data rings, grants the interface and ring pages, allocates event channels, writes grant refs/event channels/tag into Xenstore, and adds the share to `xen_9pfs_devs`. Mount creation matches the source tag and attaches the client. Requests choose a ring by tag modulo two, wait for output space, copy the 9P packet into the ring, update producer index with memory barriers, notify the backend, and drop the request reference. IRQ schedules response work, which reads headers, looks up tags, copies full replies, advances consumer index, and calls `p9_client_cb`.

State and persistence: global share list is protected by `xen_9pfs_lock`. Per-ring indexes live in shared memory; grant references and event channels persist for the lifetime of the Xen frontend device. No filesystem-level persistent state exists.

Dependencies and integration points: depends on Xenbus, Xen events, grant tables, Xen 9pfs interface helpers, workqueues, wait queues, and net/9p transport registration.

Risks: cancellation is unsupported. `p9_xen_create` attaches without setting `client->status`, relying on upper-level expectations. The request path assumes the client remains attached while scanning the global list. Ring size negotiation mutates global `p9_xen_trans.maxsize`, affecting all shares. Suspend/resume is explicitly unsupported.

Test signals: Xenstore negotiation failures, backend version/max-ring constraints, tag matching, full-ring wait/retry, malformed response lengths/tags, backend close/removal during I/O, IRQ storms/spurious interrupts, share removal while mounted, and non-Xen module load returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_xen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/Kconfig -->
# sources/distributed-fs/ceph-client/net/Kconfig

Purpose: top-level kernel networking Kconfig menu. It declares the primary `NET` option, core hidden feature flags, user-visible networking options, protocol family includes, testing options, and shared helper symbols consumed by drivers and subsystems.

Important APIs, types, and functions: this is Kconfig, so key entities are symbols rather than C APIs. Major symbols include `NET`, `COMPAT_NETLINK_MESSAGES`, `NET_INGRESS`, `NET_EGRESS`, `NET_XGRESS`, `NET_DEVMEM`, `NET_SHAPER`, `NET_CRC32C`, `NET_HANDSHAKE`, `INET`, `NETFILTER`, `BRIDGE_NETFILTER`, `MAX_SKB_FRAGS`, `RPS`, `XPS`, `CGROUP_NET_PRIO`, `CGROUP_NET_CLASSID`, `NET_PKTGEN`, `NET_DROP_MONITOR`, `WIRELESS`, `LWTUNNEL`, `PAGE_POOL`, `FAILOVER`, `ETHTOOL_NETLINK`, and KUnit-related test symbols.

Control flow: Kconfig evaluation starts at `menuconfig NET`; all nested options are active only under `if NET`. The file includes many subsystem Kconfig files in a fixed order, including `net/atm/Kconfig`, `net/appletalk/Kconfig`, `net/9p/Kconfig`, and `net/ceph/Kconfig`. Some features select lower-level dependencies, such as `NET` selecting `NLATTR`, `GENERIC_NET_UTILS`, and `BPF`; `NET_XGRESS` selecting ingress/egress; and `NET_CRC32C` selecting `CRC32`.

State and persistence: configuration state persists in the kernel `.config` and controls compile-time object inclusion and built-in/module choices. There is no runtime state in this file.

Dependencies and integration points: integrates every networking subtree into the kernel build configuration. It gates the Makefile entries researched in this subset and exposes options that alter runtime behavior across net/core, protocol families, offloads, tests, and driver helpers.

Risks: ordering matters for menu organization and dependency visibility; missing `source` entries silently hide subsystems. Incorrect `select` usage can force dependencies without their prerequisites. Compatibility symbols are explicitly discouraged for new code. `MAX_SKB_FRAGS` range changes can expose legacy driver bugs.

Test signals: `make olddefconfig`, `allyesconfig`, `allmodconfig`, and targeted configs with `NET=n`, `INET=n`, `ATLK/ATM/NET_9P` toggles. Kconfig warnings, unmet dependency reports, and expected object inclusion from `.config` are the primary validation outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/Makefile -->
# sources/distributed-fs/ceph-client/net/Makefile

Purpose: top-level networking build manifest. It maps networking Kconfig symbols to directories and object files, establishing which network subsystems are built into `net/` for a particular kernel configuration.

Important APIs, types, and functions: this is Kbuild syntax. Important entries include always-built `devres.o socket.o core/` plus unconditional `ethernet/ 802/ sched/ netlink/ bpf/ ethtool/`, and conditional directories such as `ipv4/`, `ipv6/`, `netfilter/`, `appletalk/`, `atm/`, `9p/`, `ceph/`, `wireless/`, `mac80211/`, `mptcp/`, and `shaper/`. The file uses `obj-y`, `obj-$(CONFIG_...)`, and one `ifneq ($(CONFIG_VLAN_8021Q),)` block.

Control flow: Kbuild recursively descends into directories selected by enabled symbols. `CONFIG_ATALK` controls `appletalk/`, `CONFIG_ATM` controls `atm/`, and `CONFIG_NET_9P` controls `9p/`. LLC is intentionally linked before `net/802/`, documented by a comment.

State and persistence: no runtime state; persistent effect is the build graph derived from `.config`. The order of object and directory lists affects link order for built-in networking code.

Dependencies and integration points: integrates with `net/Kconfig` and each child directory Makefile. It is the build-side counterpart to the top-level networking configuration and governs whether source files in this research set become built-in, modules, or omitted.

Risks: missing or misordered entries can break symbol resolution, init ordering, or protocol registration. The unconditional inclusion of some directories means their internal Makefiles must handle disabled features carefully. Formatting churn can obscure link-order intent.

Test signals: compare enabled `.config` symbols with `make V=1` build traversal, verify `CONFIG_ATALK=y/m`, `CONFIG_ATM=y/m`, and `CONFIG_NET_9P=y/m` pull the expected subdirectories, and build with `CONFIG_VLAN_8021Q` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/Kconfig -->
# sources/distributed-fs/ceph-client/net/appletalk/Kconfig

Purpose: declares `CONFIG_ATALK`, the AppleTalk protocol stack option.

Important APIs, types, and functions: the single symbol is `config ATALK`, a tristate user-visible option labeled "Appletalk protocol support". It selects `LLC`, enabling the lower link-layer support AppleTalk over Ethernet requires.

Control flow: when selected as built-in or module, Kbuild includes the AppleTalk directory through the top-level net Makefile. The help text describes EtherTalk and LocalTalk support, the required netatalk userspace package, and the module name `appletalk`.

State and persistence: the chosen tristate value persists in `.config` and determines whether the C files in `net/appletalk/` are compiled. Runtime state is created only by the compiled module.

Dependencies and integration points: sourced by `net/Kconfig` under `if NET`. It indirectly controls `aarp.c`, `ddp.c`, and optional proc/sysctl companion files through the AppleTalk Makefile. The `LLC` selection integrates with SNAP/LLC datalink registration used by AARP and DDP.

Risks: AppleTalk code is init-net only in the researched implementation, so enabling it in network-namespace-heavy systems does not imply per-netns support. Since the option selects LLC, dependency changes can alter build surface beyond AppleTalk itself.

Test signals: Kconfig tests should verify `ATALK=m` builds `appletalk.ko`, `LLC` is selected, and toggling `PROC_FS`/`SYSCTL` changes companion object inclusion without hiding the base protocol option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/Makefile -->
# sources/distributed-fs/ceph-client/net/appletalk/Makefile

Purpose: Kbuild manifest for the AppleTalk protocol module.

Important APIs, types, and functions: defines `obj-$(CONFIG_ATALK) += appletalk.o`, with `appletalk-y := aarp.o ddp.o`. Optional additions are `atalk_proc.o` under `CONFIG_PROC_FS` and `sysctl_net_atalk.o` under `CONFIG_SYSCTL`.

Control flow: enabling `CONFIG_ATALK` builds a composite object named `appletalk.o`. The base stack always includes AARP and DDP; procfs and sysctl interfaces are compiled only when their kernel infrastructure is enabled.

State and persistence: no runtime state in the Makefile. It persists build composition by tying object membership to `.config`.

Dependencies and integration points: aligns with `net/appletalk/Kconfig`, top-level `net/Makefile`, and conditional C preprocessor usage in `ddp.c` init/exit paths. The composite module exports symbols from DDP and AARP for AppleTalk drivers.

Risks: if `ddp.c` calls proc/sysctl init or exit helpers without matching Kbuild/preprocessor guards, configs without those options can fail. The build assumes `aarp.o` and `ddp.o` are inseparable because DDP initializes and cleans up AARP.

Test signals: build matrix with `ATALK=y/m`, `PROC_FS=y/n`, and `SYSCTL=y/n`; inspect `appletalk.o` membership; module load/unload should not reference absent optional helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/aarp.c -->
# sources/distributed-fs/ceph-client/net/appletalk/aarp.c

Purpose: implements AppleTalk Address Resolution Protocol for EtherTalk plus proxy AARP support and optional procfs reporting. It resolves AppleTalk network/node addresses to Ethernet MAC addresses and queues DDP frames while resolution is pending.

Important APIs, types, and functions: `struct aarp_entry` stores refcount, queued packets, status, expiry, target address, device, hardware address, retransmit count, and hash linkage. Global tables `resolved`, `unresolved`, and `proxies` are protected by `aarp_lock`. Externally used functions include `aarp_proto_init`, `aarp_cleanup_module`, `aarp_send_ddp`, `aarp_device_down`, `aarp_probe_network`, `aarp_proxy_probe_network`, and `aarp_proxy_remove`.

Control flow: `aarp_send_ddp` handles LocalTalk and PPP directly, sends AppleTalk broadcast frames to the multicast address, looks up resolved Ethernet mappings, queues packets on unresolved entries, and sends AARP requests. The timer expires resolved/proxy entries and retransmits unresolved queries until `sysctl_aarp_retransmit_limit`. `aarp_rcv` handles AARP replies, requests, and probes; replies resolve queued packets, while requests/probes for local or proxy addresses trigger replies and may flush stale cache entries.

State and persistence: global hash tables and the timer are module-local. Tunables `sysctl_aarp_expiry_time`, `sysctl_aarp_tick_time`, `sysctl_aarp_retransmit_limit`, and `sysctl_aarp_resolve_time` are mutable via sysctl when enabled. State is runtime-only and scoped to `init_net`.

Dependencies and integration points: depends on SNAP registration (`register_snap_client`), DDP datalink operations, netdevice notifier events, AppleTalk interface lookup from DDP, Ethernet helpers, timers, and optional proc seq operations (`aarp_seq_ops`).

Risks: one global rwlock protects all tables and is used in softirq contexts with atomic allocations. `unresolved_count` must stay balanced; unresolved entries queue skbs and can drop traffic under memory pressure. Proxy probing temporarily releases and reacquires locks while retaining entry references. The code does not use generic neighbour infrastructure.

Test signals: AARP request/reply/probe exchange, duplicate address detection, proxy add/remove, device down purging, sysctl timer changes, proc `atalk/arp` iteration, queued packet release on resolution, retransmit-limit expiry, and non-init-net packet rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/aarp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/atalk_proc.c -->
# sources/distributed-fs/ceph-client/net/appletalk/atalk_proc.c

Purpose: provides `/proc/net/atalk/*` seq_file views for AppleTalk interfaces, routes, sockets, and AARP entries.

Important APIs, types, and functions: interface, route, and socket seq operation sets are `atalk_seq_interface_ops`, `atalk_seq_route_ops`, and `atalk_seq_socket_ops`. Public lifecycle functions are `atalk_proc_init` and `atalk_proc_exit`. It also references `aarp_seq_ops` for `/proc/net/atalk/arp`.

Control flow: init creates the `atalk` proc directory under `init_net.proc_net`, then creates `interface`, `route`, `socket`, and `arp` entries. Each seq iterator takes the matching global AppleTalk lock in `start`, walks a linked list or hlist in `next`, formats rows in `show`, and releases the lock in `stop`. Failure during creation removes the entire `atalk` subtree.

State and persistence: no independent protocol state; it reads DDP global lists (`atalk_interfaces`, `atalk_routes`, `atalk_sockets`, and `atrtr_default`) and AARP global tables. Proc entries exist only while the module is loaded and `CONFIG_PROC_FS` is enabled.

Dependencies and integration points: depends on procfs, seq_file, init_net proc namespace, DDP locks and structures, socket ownership helpers, and AARP iterator private state for the `arp` file.

Risks: output is init-net only. Route display emits the default route inside every non-header route row when `atrtr_default.dev` is set, which can duplicate default output during iteration. Long-held read locks while formatting can block writers for large tables.

Test signals: module init failure unwinding, reading all proc files while interfaces/routes/sockets/AARP entries change, namespace behavior, permission mode `0444`, and lockdep during concurrent ioctls and proc reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/atalk_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/ddp.c -->
# sources/distributed-fs/ceph-client/net/appletalk/ddp.c

Purpose: implements the AppleTalk Datagram Delivery Protocol socket family, interface/routing ioctls, packet receive/routing/send paths, and module lifecycle for the Linux AppleTalk stack.

Important APIs, types, and functions: global state includes `atalk_sockets`, `atalk_routes`, `atalk_interfaces`, and `atrtr_default` with rwlocks. Exports are `atrtr_get_dev` and `atalk_find_dev_addr`. Important internals include `atalk_create`, `atalk_bind`, `atalk_connect`, `atalk_sendmsg`, `atalk_recvmsg`, `atalk_rcv`, `ltalk_rcv`, `atif_ioctl`, `atrtr_create`, `atrtr_delete`, `atalk_route_packet`, and `atalk_init`/`atalk_exit`.

Control flow: module init registers the DDP proto and PF_APPLETALK family, registers SNAP DDP, LocalTalk, and PPP packet handlers, installs a device notifier, initializes AARP, procfs, and sysctl. Interface ioctls add AppleTalk addresses, probe via AARP, create direct routes, and join multicast. Sendmsg autobinds if needed, looks up routes, builds DDP headers/checksums, handles broadcast loopback, and delegates link-layer delivery to `aarp_send_ddp`. Receive validates length and checksum, finds a local interface/socket, queues to the socket, or routes the packet onward with hop-count enforcement.

State and persistence: all sockets, interfaces, routes, and default router are runtime global init-net state. Device references are held for interfaces/routes. Socket lifecycle removes from global hlist and defers destruction until allocations drain.

Dependencies and integration points: depends on LLC/SNAP datalink, AARP, netdevice notifier, socket core, rtnl for interface ioctls, proc/sysctl optional helpers, and packet handlers for LocalTalk/PPP encapsulations.

Risks: namespace support is intentionally absent for non-init_net sockets and packets. Routing/interface state uses linked lists and global locks, so scaling is limited. Route creation must maintain device refs correctly. Legacy ioctls and compat conversions are broad attack surface. Packet routing mutates shared skb data and has comments noting limitations around `skb->cb`.

Test signals: PF_APPLETALK socket creation/bind/connect/send/recv, raw socket permission checks, interface add/delete with AARP probe success/failure, route add/delete, LocalTalk short-header expansion, checksum failures, broadcast loopback, packet forwarding hop limit, compat ioctls, device-down cleanup, and full init failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/ddp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/sysctl_net_atalk.c -->
# sources/distributed-fs/ceph-client/net/appletalk/sysctl_net_atalk.c

Purpose: exposes AppleTalk AARP timing and retry tunables through `/proc/sys/net/appletalk`.

Important APIs, types, and functions: `atalk_table` contains four `ctl_table` entries: `aarp-expiry-time`, `aarp-tick-time`, `aarp-retransmit-limit`, and `aarp-resolve-time`. Lifecycle functions are `atalk_register_sysctl` and `atalk_unregister_sysctl`.

Control flow: registration calls `register_net_sysctl(&init_net, "net/appletalk", atalk_table)` and stores the returned header. Unregistration passes that header to `unregister_net_sysctl_table`. Time values use `proc_dointvec_jiffies`; retransmit limit uses `proc_dointvec`.

State and persistence: the sysctl values point directly at global integers defined in `aarp.c`. They persist only while the module is loaded and are init-net sysctls, not per-network-namespace state.

Dependencies and integration points: depends on `CONFIG_SYSCTL`, the sysctl core, init_net, and AARP global tunables. DDP module init/exit calls these helpers when sysctl support is compiled.

Risks: no min/max validation is defined in the table, so unreasonable values can affect timer cadence, cache lifetime, and retransmission behavior. A missing registration header would make unregister unsafe if called after failed registration, though the normal init path only calls exit after success.

Test signals: sysctl directory creation/removal, read/write conversion for jiffies-based values, behavior with zero or very large timer values, and module init unwind when sysctl registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/appletalk/sysctl_net_atalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/Kconfig -->
# sources/distributed-fs/ceph-client/net/atm/Kconfig

Purpose: declares the core ATM protocol option and RFC2684 bridging/routed-over-ATM options.

Important APIs, types, and functions: key symbols are `ATM`, `ATM_BR2684`, and `ATM_BR2684_IPFILTER`. `ATM` is a tristate for the Asynchronous Transfer Mode networking core. `ATM_BR2684` is a tristate depending on `ATM && INET`. `ATM_BR2684_IPFILTER` is a bool depending on `ATM_BR2684`.

Control flow: when sourced by top-level `net/Kconfig`, these symbols control inclusion of the ATM core composite object and optional `br2684.o`. The BR2684 option enables an Ethernet-like or routed netdevice over ATM PVCs; the IP filter option enables an experimental per-VC filter ioctl and receive-path filtering.

State and persistence: configuration persists in `.config`; no runtime state is held in this file.

Dependencies and integration points: coordinates with `net/atm/Makefile`, ATM socket core, ATM drivers, INET protocol support, and userspace tooling documented by the help text.

Risks: BR2684 depends on INET because routed and bridged packet handling uses IP/Ethernet semantics. Enabling experimental IP filtering adds receive-path policy code with limited scope and should be treated as a compatibility feature.

Test signals: build matrices for `ATM=y/m`, `ATM_BR2684=y/m/n`, and `ATM_BR2684_IPFILTER=y/n`; verify dependency enforcement when `INET=n`; ensure module names and object inclusion match the selected tristates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/Makefile -->
# sources/distributed-fs/ceph-client/net/atm/Makefile

Purpose: Kbuild manifest for ATM protocol families and optional ATM protocol adapters.

Important APIs, types, and functions: defines composite `atm-y` as `addr.o pvc.o signaling.o svc.o ioctl.o common.o atm_misc.o raw.o resources.o atm_sysfs.o`. `obj-$(CONFIG_ATM) += atm.o`; `obj-$(CONFIG_ATM_BR2684) += br2684.o`; optional `atm-$(CONFIG_PROC_FS) += proc.o`; and `obj-$(CONFIG_PPPOATM) += pppoatm.o`.

Control flow: enabling core ATM builds the composite `atm.o` from common socket code, address registry, signaling, resources, sysfs, and protocol adapters. Proc support is included only with procfs. BR2684 and PPP-over-ATM are separate objects/modules gated by their symbols.

State and persistence: no runtime state; build composition is derived from `.config`.

Dependencies and integration points: matches `net/atm/Kconfig` and the top-level net Makefile. The composition assumes `common.o` can call helpers from sibling ATM objects and that optional modules such as BR2684 register with ATM ioctl/notifier hooks exported by the core.

Risks: object membership and link order matter because `subsys_initcall(atm_init)` and protocol initialization call into the included objects. Optional proc/sysfs dependencies must stay aligned with C references.

Test signals: `ATM=y/m` builds `atm.o` with all base members, `PROC_FS=n` omits `proc.o`, `ATM_BR2684=m` builds `br2684.ko`, and link checks confirm exported hooks satisfy BR2684/PPPOATM users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/addr.c -->
# sources/distributed-fs/ceph-client/net/atm/addr.c

Purpose: manages local ATM service addresses associated with an `atm_dev`, including normal local addresses and LECS addresses.

Important APIs, types, and functions: public functions are `atm_reset_addr`, `atm_add_addr`, `atm_del_addr`, and `atm_get_addr`, declared in `addr.h`. Helpers `check_addr`, `identical`, and `notify_sigd` validate addresses, compare private/public address fields, and notify the ATM signaling daemon of interface address changes.

Control flow: add/delete validate `sockaddr_atmsvc`, select either `dev->lecs` or `dev->local`, take `dev->lock`, check for duplicates or matching entries, mutate the list, release the lock, and notify signaling for local address changes. Reset removes all entries from the selected list. Get counts entries under lock, copies them to a temporary buffer, then copies as many as fit to userspace.

State and persistence: state is the `atm_dev_addr` list entries stored on each `atm_dev`. It is runtime-only and protected by the device spinlock. Local address changes trigger `sigd_enq(... as_itf_notify ...)`.

Dependencies and integration points: depends on ATM core structures, signaling (`sigd_enq`), `copy_to_user`, and list operations. Used by ATM ioctl/resource paths to maintain addresses visible through sysfs and signaling.

Risks: `atm_get_addr` allocates `total` bytes while holding a spinlock with `GFP_ATOMIC`; very large address lists can fail. It copies `min(total, size)` but returns `-E2BIG` when user buffer is too small. Address validation relies on public address NUL termination and private-address first byte semantics.

Test signals: add duplicate addresses, delete missing addresses, reset local versus LECS lists, query with exact/small/large user buffers, signaling notification on local changes only, invalid family/public-string termination, and concurrent sysfs/ioctl reads under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/addr.h -->
# sources/distributed-fs/ceph-client/net/atm/addr.h

Purpose: internal header declaring the ATM local address registry interface implemented by `addr.c`.

Important APIs, types, and functions: declares `atm_reset_addr`, `atm_add_addr`, `atm_del_addr`, and `atm_get_addr`, all operating on `struct atm_dev`, `struct sockaddr_atmsvc`, and `enum atm_addr_type_t`.

Control flow: no executable flow. The prototypes define the contract for callers to reset, add, delete, or retrieve per-device ATM addresses.

State and persistence: no state is stored in the header. The state contract is the caller-visible mutation of `atm_dev` address lists.

Dependencies and integration points: includes `<linux/atm.h>` and `<linux/atmdev.h>`, so callers receive ATM socket/device definitions. Used by ATM core files such as `common.c` and ioctl/resource code that need address registry operations.

Risks: since this is a narrow internal header, risk comes from signature drift: changes must be synchronized with `addr.c` and all callers. User pointer annotation on `atm_get_addr` documents that the function performs userspace copy.

Test signals: compile coverage is the main signal; any prototype mismatch will break the ATM composite build. Sparse/usercopy checks should respect the `__user` annotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/atm_misc.c -->
# sources/distributed-fs/ceph-client/net/atm/atm_misc.c

Purpose: provides small exported helper routines for ATM drivers and protocol adapters, covering receive-buffer accounting, PCR selection, and SONET statistics conversion.

Important APIs, types, and functions: exported helpers are `atm_charge`, `atm_alloc_charge`, `atm_pcr_goal`, `sonet_copy_stats`, and `sonet_subtract_stats`.

Control flow: `atm_charge` force-charges receive memory to the VCC socket, checks against `sk_rcvbuf`, and either keeps the charge or returns it and increments `rx_drop`. `atm_alloc_charge` estimates skb truesize, charges first, allocates the skb, adjusts accounting to actual truesize, or rolls back on failure. `atm_pcr_goal` converts ATM traffic parameters into a positive, negative, or zero PCR target describing rounding direction or maximum bandwidth. SONET helpers copy/subtract atomic stats through the `__SONET_ITEMS` macro list.

State and persistence: no independent state. It mutates per-socket receive accounting and VCC statistics counters provided by callers.

Dependencies and integration points: exported to ATM drivers and modules that receive cells/PDUs and need consistent socket buffer accounting. Relies on `atm_force_charge`, `atm_return`, `sk_atm`, skb allocation, and SONET stat definitions.

Risks: accounting correctness is critical; double charging or missing rollback can create memory pressure or false leakage warnings. `atm_alloc_charge` uses an estimate before allocation and must compensate for actual skb truesize. PCR sign semantics are compact and easy for callers to misuse.

Test signals: receive path under small `sk_rcvbuf`, allocation failure injection, rx_drop counter increments, accounting returning to zero after skb free, PCR table cases from the comment, and SONET stat copy/subtract with nonzero atomic counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/atm_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/atm_sysfs.c -->
# sources/distributed-fs/ceph-client/net/atm/atm_sysfs.c

Purpose: registers the ATM device class and exposes per-ATM-device attributes in sysfs.

Important APIs, types, and functions: attribute show functions include `type_show`, `address_show`, `atmaddress_show`, `atmindex_show`, `carrier_show`, and `link_rate_show`. Lifecycle functions are `atm_register_sysfs`, `atm_unregister_sysfs`, `atm_sysfs_init`, and `atm_sysfs_exit`. `atm_class` defines `.dev_release` and `.dev_uevent`.

Control flow: class init registers `atm_class`. Device registration initializes `adev->class_dev`, sets class/parent/driver data/name, calls `device_register`, then creates each attribute file. Failure removes already-created files and deletes the device. Unregistration calls `device_del`; object memory is freed by class release when the device refcount reaches zero.

State and persistence: sysfs state mirrors `struct atm_dev` fields: type, ESI MAC-like address, local ATM service addresses, device number, signal-derived carrier, and link rate. It is runtime sysfs state, not durable storage.

Dependencies and integration points: depends on device model class registration, ATM resources, `atm_dev` locks/address lists, and uevent environment construction. Userspace can discover devices through `/sys/class/atm` and uevents with `NAME=<type><number>`.

Risks: `atmaddress_show` formats all local addresses into one PAGE_SIZE buffer; many addresses can truncate output. `atm_register_sysfs` calls `device_del` on attribute failure but not `put_device`, so lifetime expectations depend on surrounding ATM registration code. Link-rate conversion has special cases and a generic cell-rate conversion.

Test signals: device register/unregister, sysfs attributes with zero/multiple local addresses, carrier changes after `atm_dev_signal_change`, uevent content, failure injection during attribute creation, and KASAN/refcount checks around class release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/atm_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/br2684.c -->
# sources/distributed-fs/ceph-client/net/atm/br2684.c

Purpose: implements RFC1483/RFC2684 bridged or routed Ethernet/IP-style netdevices over ATM AAL5 VCCs, commonly used for DSL PVC-backed interfaces.

Important APIs, types, and functions: `struct br2684_dev` stores the netdevice, device number, attached VCC list, MAC configuration flag, and payload mode. `struct br2684_vcc` stores the ATM VCC, netdevice, chained callbacks, encapsulation mode, queue space, and optional IP filter. Key functions include `br2684_create`, `br2684_regvcc`, `br2684_start_xmit`, `br2684_xmit_vcc`, `br2684_push`, `br2684_pop`, `br2684_close_vcc`, `br2684_ioctl`, and `br2684_init`/`br2684_exit`.

Control flow: userspace creates a netdevice with `ATM_NEWBACKENDIF` and attaches a connected ATM socket with `ATM_SETBACKEND`. Registration chains the VCC push/pop/release callbacks, sets ATM skb ownership, initializes carrier state, and reprocesses queued receive skbs. TX chooses the first attached VCC, validates VCC readiness, prepends LLC/SNAP or VC padding headers depending on routed/bridged mode, accounts TX, and calls the ATM device send operation. RX strips and validates encapsulation, optionally filters IP traffic, updates stats, and injects packets with `netif_rx`. A `NULL` push means the VCC is being destroyed and triggers device cleanup when no VCCs remain.

State and persistence: global `br2684_devs` and per-device VCC lists are protected by `devs_lock`. Per-VCC `qspace` throttles the netdev queue to about two ATM packets. Procfs state reports devices, VCCs, encapsulation, payload mode, copy failures, and optional filters.

Dependencies and integration points: depends on ATM core ioctl registration/notifier APIs, netdevice core, Ethernet helpers, rtnetlink conventions, ATM backend userspace ABI, optional procfs, and optional `CONFIG_ATM_BR2684_IPFILTER`.

Risks: only one VCC per device is supported despite list structure. Callback chaining and module-owner swapping are delicate; close paths must restore callbacks and module refs. Receive encapsulation parsing accepts several legacy variants but drops malformed frames. Queue throttling can race with ATM pop callbacks. Exit forcibly unregisters all devices.

Test signals: create bridged and routed devices, attach duplicate VCCs, send IPv4/IPv6/unsupported payloads over LLC and VC encapsulation, receive malformed headers/FCS padding, carrier changes from ATM notifier, queue stop/wake behavior, proc output, IP filter behavior, and module unload with active devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/br2684.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/common.c -->
# sources/distributed-fs/ceph-client/net/atm/common.c

Purpose: core ATM socket/VCC implementation shared by PVC and SVC protocol families. It handles VCC allocation, connection, send/receive, QoS options, socket polling, device-signal notification, and module initialization.

Important APIs, types, and functions: exported globals are `vcc_hash` and `vcc_sklist_lock`. Exported functions include `vcc_insert_socket`, `vcc_release_async`, `vcc_process_recv_queue`, `atm_dev_signal_change`, `atm_dev_release_vccs`, `register_atmdevice_notifier`, and `unregister_atmdevice_notifier`. Core socket operations are `vcc_create`, `vcc_release`, `vcc_connect`, `vcc_recvmsg`, `vcc_sendmsg`, `vcc_poll`, `vcc_setsockopt`, and `vcc_getsockopt`.

Control flow: `vcc_create` allocates a `struct atm_vcc` socket, initializes callbacks, QoS defaults, accounting, and flags. `vcc_connect` validates socket state and QoS, looks up or requests an ATM device, reserves a VPI/VCI with collision checks in `vcc_hash`, initializes the requested AAL, adjusts traffic parameters, and calls the driver `open` operation. Send waits for TX accounting space, allocates and fills an skb, optionally calls driver `pre_send`, and invokes driver `send`. Receive pulls datagrams from the socket queue, copies to userspace, and returns receive memory accounting unless peeking. Release closes the VCC, calls driver close and push(NULL), drains queues, drops module/device refs, and removes the socket from the hash.

State and persistence: VCCs are stored in a hash by VCI and protected by `vcc_sklist_lock`. Each VCC tracks device, VPI/VCI, QoS, flags such as `ATM_VF_READY/CLOSE/WAITING/PARTIAL`, callbacks, owner modules, and socket memory accounting. Device notifier chain state is runtime-only.

Dependencies and integration points: depends on ATM resource lookup, PVC/SVC init paths, signaling, AAL protocol initialization, socket core, usercopy, poll, module autoloading, proc/sysfs initialization, and optional backend modules such as BR2684.

Risks: VPI/VCI allocation uses static scan cursors shared across devices. VCC hash collision rules allow shared VPI/VCI only when TX/RX classes do not collide. Send/receive accounting must balance with driver callbacks. Async release removes sockets from hash while waking userspace. QoS changes after connect are intentionally constrained.

Test signals: PF_ATMPVC/PF_ATMSVC socket create/connect/release, QoS validation and change, ANY VPI/VCI allocation, reserved VCI permission checks, send blocking and `MSG_DONTWAIT`, receive `MSG_PEEK`, poll masks, device removal via `atm_dev_release_vccs`, notifier callbacks, AAL0/AAL5/AAL34 selection, and init failure unwinding across proto/PVC/SVC/proc/sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/common.c -->
