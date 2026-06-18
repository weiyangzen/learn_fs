# sources/distributed-fs/ceph-client/net/packet/af_packet.c

## Purpose
`af_packet.c` implements Linux AF_PACKET raw packet sockets, including legacy `SOCK_PACKET`, `SOCK_RAW` and `SOCK_DGRAM` packet sockets, classic queued receive, memory-mapped TPACKET RX/TX rings, fanout groups, device membership management, procfs reporting, and PF_PACKET module/per-net registration. It is the user/kernel boundary for sniffers, packet injectors, zero-copy capture/transmit tools, and packet fanout consumers.

## Important APIs, types, and functions
The file builds on `struct packet_sock`, `struct packet_ring_buffer`, `struct packet_fanout`, and `struct packet_rollover` from `internal.h`. Socket operations are exported through `packet_ops` and `packet_ops_spkt`, family creation through `packet_family_ops`, and per-net `/proc/net/packet` support through `packet_net_ops`.

Receive entry points are `packet_rcv_spkt()`, `packet_rcv()`, and `tpacket_rcv()`. `packet_rcv()` queues cloned/truncated skbs on the normal receive queue after BPF filtering, address metadata setup, drop accounting, and conntrack/dst cleanup. `tpacket_rcv()` writes directly into user-mmaped TPACKET frames or V3 blocks, handling snap length, offsets, VLAN/checksum/timestamp metadata, optional copy fallback, and frame/block ownership transitions.

Transmit entry points are `packet_sendmsg_spkt()`, `packet_snd()`, and `tpacket_snd()`. `packet_snd()` allocates an skb from the message iterator, optionally parses virtio-net headers, builds L2 headers for DGRAM sockets, validates MTU and headers, and calls `packet_xmit()`. `tpacket_snd()` walks TX ring frames marked `TP_STATUS_SEND_REQUEST`, builds skb fragments backed by mapped ring pages, marks frames `TP_STATUS_SENDING`, and returns them to userspace in `tpacket_destruct_skb()`.

Ring setup and mmap are centralized in `packet_set_ring()`, `alloc_pg_vec()`, `free_pg_vec()`, and `packet_mmap()`. TPACKET_V3 block logic uses `init_prb_bdqc()`, `prb_open_block()`, `prb_dispatch_next_block()`, `prb_retire_current_block()`, and `prb_retire_rx_blk_timer_expired()` to manage block fill, timeout retirement, and user/kernel ownership.

Fanout support is implemented by `fanout_add()`, `packet_rcv_fanout()`, the `fanout_demux_*()` helpers, `fanout_set_data_*()` for CBPF/EBPF fanout programs, and `fanout_release()`. Socket/device attachment is controlled by `packet_do_bind()`, `__register_prot_hook()`, `__unregister_prot_hook()`, and `packet_notifier()`.

## Control flow and state
Creation requires `CAP_NET_RAW`, allocates `packet_sock` via `sk_alloc()`, initializes `bind_lock`, `pg_vec_lock`, pending TX refcounts, protocol hooks, cached-device RCU pointer, and optionally registers the packet hook immediately when the protocol is nonzero. Binding under `bind_lock` resolves the requested device/protocol, unregisters any old hook with `synchronize_net()` when needed, updates `po->prot_hook`, `po->ifindex`, `po->num`, and `po->cached_dev`, then registers the hook if the device is usable.

Normal receive flow rejects loopback and wrong namespace traffic, adjusts headers according to socket type and device header visibility, runs socket BPF, enforces receive memory, snapshots source metadata into `PACKET_SKB_CB`, trims to snap length, queues the skb, and wakes waiters. TPACKET receive follows the same filtering and header adjustment, but reserves a ring frame/block, copies packet bytes into mapped memory, writes per-version headers, publishes status with memory barriers and cache flushes, and updates packet/drop stats.

TPACKET_V3 state is block-oriented. The current block starts as `TP_STATUS_KERNEL`, packet additions update `nxt_offset`, `prev`, `BLOCK_NUM_PKTS`, and `BLOCK_LEN`, and block retirement publishes `TP_STATUS_USER` plus loss/timeout flags. A soft hrtimer periodically retires partially filled blocks. If userspace has not returned the next block, `prb_freeze_queue()` marks the queue frozen and increments `tp_freeze_q_cnt`; later receive or timer activity reopens the block when ownership returns.

Transmit flow chooses between ring and non-ring paths. The ring path serializes with `pg_vec_lock`, resolves the target device from the cached bind or send address, parses per-frame packet length/offsets, builds an skb using ring pages as frags, optionally converts virtio-net metadata, marks the frame as sending, queues/direct-xmits, advances the TX ring head, and relies on the skb destructor to restore frame availability and wake blocked senders.

Lifecycle cleanup removes the socket from the per-net list, unregisters hooks, drops cached device references, flushes multicast memberships, tears down RX/TX rings while holding the socket lock, releases fanout membership after `synchronize_net()`, purges queues, frees pending refcounts, and drops the final sock reference.

## State and persistence behavior
State is in-memory only: socket configuration, multicast memberships, ring pages, fanout groups, cached device references, and stats live in kernel memory and disappear when sockets/modules/net namespaces are destroyed. `/proc/net/packet` is a read-only live view. `PACKET_STATISTICS` is clear-on-read for drops and packet counts. Mapped ring pages persist while the socket and VMAs are alive; `mapped` prevents unsafe ring reconfiguration.

Concurrency relies on `bind_lock` for packet hook/device/protocol state, `pg_vec_lock` for ring pointer and mmap reconfiguration, sk receive/write queue locks for ring head/status operations, RCU for live packet hooks and cached devices, `fanout_mutex` plus per-fanout spinlocks for group membership, and refcounts/completions for TX ring pending packets.

## Dependencies and integration points
The file integrates with the netdevice packet tap API (`dev_add_pack`, `__dev_remove_pack`), netdevice notifier chain, rtnetlink-visible devices, BPF socket filters, optional fanout BPF programs, netfilter egress when qdisc bypass is enabled, virtio-net header helpers, VLAN helpers, timestamping/error queue APIs, per-net procfs, generic datagram receive/poll, and capability checks. It depends on UAPI packet socket definitions such as `struct tpacket_req`, `TP_STATUS_*`, `PACKET_*` sockopts, and `sockaddr_ll`.

## Risks and edge cases
This file has high race and memory-safety sensitivity. Important risks include ring ownership races across userspace mmap and softirq receive, stale device pointers during unregister/down/up events, fanout membership changes while packets are in flight, V3 block timeout races with `skb_copy_bits()`, integer overflow in ring geometry, and status publication ordering between kernel and userspace. The code uses explicit barriers, cache flushes, RCU synchronization, and busy checks, but changes in these areas need careful packetdrill/selftest coverage.

User-controlled ring geometry, offsets, virtio-net header size, multicast requests, fanout options, and raw frame bytes are heavily validated; regressions could expose kernel memory corruption or packet injection bugs. Another operational risk is behavior compatibility: AF_PACKET is used by tcpdump, container runtimes, DHCP tools, traffic generators, and security agents, so changes to header offsets, auxdata, VLAN metadata, or fanout semantics can break existing tooling.

## Test signals
Useful tests include AF_PACKET kselftests, packet socket fanout tests, mmap RX/TX ring tests for TPACKET_V1/V2/V3, BPF filter and fanout CBPF/EBPF tests, VLAN auxdata checks, qdisc bypass/netfilter egress checks, netdev unregister/down/up while sockets are bound, namespace isolation tests, and stress tests with concurrent mmap close, ring reconfiguration, poll, send, and receive. Runtime signals include `/proc/net/packet`, `PACKET_STATISTICS`, drop counters, fanout rollover stats, `strace` of packet sockopts, and packet capture validation under tcpdump/libpcap.
