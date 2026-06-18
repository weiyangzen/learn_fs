# sources/distributed-fs/ceph-client/tools/perf/scripts/python/netdev-times.py

Purpose: `netdev-times.py` reconstructs RX and TX packet processing timelines from IRQ, softirq, NAPI, net, and skb tracepoints, making network device latency visible in a textual chart.

Important APIs and state: perf callbacks append normalized event tuples to `all_event_list`. Handler functions then correlate them into `irq_dic`, `net_rx_dic`, `receive_hunk_list`, `rx_skb_list`, `tx_queue_list`, `tx_xmit_list`, and `tx_free_list`. Options parsed from `sys.argv` select TX/RX output, device filtering, and debug buffer status.

Control flow: callbacks only collect event data. `trace_end` sorts collected events by timestamp and dispatches to handlers that build receive hunks around NET_RX softirq windows and transmit records from queue to xmit to free. RX output prints IRQ entry, netif_rx, softirq entry, NAPI poll, netif_receive_skb, copy, free, or consume events relative to the first IRQ timestamp. TX output prints queue-to-driver and driver-to-free latencies.

State and persistence: all correlation state is in memory. The script enforces fixed budgets for RX, TX queue, and TX xmit lists and increments overflow counters when old unmatched records are dropped.

Dependencies, integration, risks, and tests: it relies on perf's trace utility modules, symbol decoding for `NET_RX`, and tracepoint field compatibility across kernel versions. Risks include high memory use from `all_event_list`, fragile stack matching for nested IRQs, correlation loss under buffer overflow, and a comparator-style sort lambda that returns booleans rather than a three-way compare. Test signals are realistic RX/TX traces where skb addresses match across tracepoints and debug mode reports low overflow counts.
