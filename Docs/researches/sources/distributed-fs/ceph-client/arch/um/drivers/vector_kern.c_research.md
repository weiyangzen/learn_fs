<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.c

Purpose: implements UML high-performance vector network devices (`vecN`) using batch send/receive syscalls and transport-specific host sockets. It supports vector or legacy RX/TX, NAPI, BQL, ethtool stats/coalescing/BPF firmware loading, mconsole dynamic config, and transports implemented by `vector_user.c`/`vector_transports.c`.

Important APIs/types/functions: key structs are `vector_cmd_line_arg`, `vector_device`, `vector_queue`, `vector_private`, and `vector_estats`. Major functions include option parsers (`get_mtu()`, `get_depth()`, `get_transport_options()`), queue management (`create_queue()`, `destroy_queue()`, `vector_enqueue()`, `vector_send()`, `prep_skb()`, `vector_mmsg_rx()`), netdev ops (`vector_net_open()`, `vector_net_close()`, `vector_net_start_xmit()`, `vector_poll()`, `vector_net_tx_timeout()`), ethtool ops, config functions (`vector_parse()`, `vector_config()`, `vector_remove()`), and init functions (`vector_setup()`, `vector_init()`, `vector_net_init()`).

Control flow: boot `vecN:key=value,...` arguments are stored early and parsed at late init; mconsole config can add devices later. Device configuration allocates an Ethernet netdev, sets MTU/MAC/options, registers a platform device and netdevice, and stores parsed args. Open loads optional BPF, opens host FDs, builds transport data, creates RX/TX vector queues or legacy buffers, registers NAPI and read/write IRQs, attaches BPF if needed, starts the queue, and schedules NAPI to drain preexisting host data. TX either writes one packet with writev or enqueues skb/iov entries for sendmmsg, using a timer for coalescing. RX uses recvmmsg into prepared skbs or legacy recvmsg, verifies transport headers, trims encapsulation, updates stats, and delivers with GRO.

State and persistence: runtime state includes registered vector devices list, parsed boot args, per-netdev FDs, IRQs, queues, skbs/iov arrays, transport data, BPF program, timers, NAPI state, and ethtool stats. No persistent network state is stored.

Dependencies and integration points: depends on Linux netdev/NAPI/ethtool/BQL/firmware APIs, UML IRQ/FD helpers, `vector_user.h` host socket helpers, `build_transport_data()`, mconsole, and optional inetaddr notifier.

Risks: queue ownership spans hard IRQ, NAPI, timers, and netdev close. RX queue comments note it is not a conventional wraparound queue. Error state deactivates FDs and can leave TX busy until reset/close. BPF firmware loading via ethtool is gated but powerful. Some error paths in `vector_eth_configure()` return without freeing partially registered platform resources.

Test signals: configure tap/raw/hybrid/GRE/L2TPv3/BESS devices, vector and legacy modes, ping/throughput tests, GRO/TSO/vnet-header toggles, BPF default/user/flash attach, ethtool stats/ring/coalesce, TX timeout recovery, mconsole add/remove, close/reopen, and host socket EAGAIN/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.c -->
