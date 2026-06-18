# sources/distributed-fs/ceph-client/include/linux/netpoll.h

Purpose: Declares netpoll support for emergency UDP network I/O from constrained contexts such as console, panic, and crash paths.

Important APIs, types, and functions: Key types are `union inet_addr`, `struct netpoll`, and `struct netpoll_info`; APIs include poll disable/enable, `netpoll_send_udp()`, setup/free/cleanup helpers, poll locking, and TX-running checks. Detected source surface: 121 lines; includes `linux/interrupt.h`, `linux/list.h`, `linux/netdevice.h`, `linux/rcupdate.h`, `linux/refcount.h`; macros `_LINUX_NETPOLL_H`, `np_err`, `np_info`, `np_notice`; structs `delayed_work`, `in6_addr`, `napi_struct`, `net_device`, `netpoll`, `netpoll_info`, `rcu_head`, `semaphore`, `sk_buff_head`, `work_struct`; enums none; typedefs none; function-like declarations/helpers `__netpoll_free`, `__netpoll_setup`, `do_netpoll_cleanup`, `irqs_disabled`, `netpoll_cleanup`, `netpoll_poll_dev`, `netpoll_poll_disable`, `netpoll_poll_enable`, `netpoll_poll_unlock`, `netpoll_send_skb`, `netpoll_send_udp`, `netpoll_setup`, `netpoll_tx_running`, `smp_store_release`.

Control flow: A configured netpoll endpoint stores local/remote addresses, ports, MAC address, and device; send paths bypass normal process context where possible and poll device/NAPI state under netpoll locks.

State and persistence behavior: Per-netpoll endpoint state persists for the configured device and target. Per-device `netpoll_info` tracks refcount, cleanup work, rx/tx state, and napi ownership.

Dependencies and integration points: Depends on netdevice, interrupts, RCU, lists, and refcounts. Integrated by netconsole and emergency logging paths.

Risks and test signals: Risks are deadlocks with NAPI/device locks, use-after-free during device teardown, and packet loss under panic constraints. Test setup/cleanup, device unregister, high-rate console output, and lockdep under netpoll transmission.
