# sources/distributed-fs/openafs/src/rx/LINUX/rx_knet.c

Purpose: Linux Rx kernel socket implementation for opening UDP sockets, sending/receiving packets, handling error queues, and stopping the listener.

Important APIs/types/functions: `rxk_NewSocketHost`, `rxk_NewSocket`, `rxk_FreeSocket`, optional `osi_HandleSocketError`, `osi_NetSend`, `osi_NetReceive`, and `osi_StopListener`.

Control flow: socket creation chooses the available `sock_create_kern`/`sock_create` variant, binds IPv4 UDP, configures PMTU discovery and optional `IP_RECVERR`. Send builds an `msghdr` and calls `kernel_sendmsg`. Receive calls `kernel_recvmsg`; on errors it freezes if needed, flushes signals, records counters, and drains async socket errors. Stop kills the listener task until it exits, then releases `rx_socket`.

State/persistence: Linux socket object, socket error counters, listener task pointer, PMTU/recv-error socket options.

Dependencies/integration: Linux socket APIs, OpenAFS compatibility wrappers, Rx stats/error processing, and listener thread lifecycle.

Risks: kernel API signatures vary widely; `struct iovec` cast to `struct kvec` assumes layout compatibility; killing the listener must not race with socket release; async ICMP processing depends on control buffer sizing. Test signals are kernel-version builds, send/receive loopback, PMTU adaptation, ICMP error queue processing, and listener shutdown.
