# sources/distributed-fs/ceph-client/drivers/net/xen-netback/interface.c

Purpose: This file owns the Linux `net_device` interface layer for Xen netback VIFs. It allocates and registers backend Ethernet devices, routes host TX packets into per-queue guest RX queues, exposes queue statistics through ethtool, and connects/disconnects Xen data and control rings to IRQs, NAPI, and backend kthreads.

Important APIs, types, and functions: `xenvif_alloc()` builds the `vif<domid>.<handle>` netdev and initializes `struct xenvif`; `xenvif_init_queue()` reserves grant-table mapping pages and queue rings; `xenvif_connect_data()` maps frontend TX/RX rings, creates RX and deallocation kthreads, installs NAPI, and binds split or shared event channels; `xenvif_connect_ctrl()` maps the control ring; `xenvif_start_xmit()` queues host SKBs for delivery to the frontend; `xenvif_up()`, `xenvif_down()`, `xenvif_carrier_on()`, and `xenvif_carrier_off()` bridge netdev state to backend queue state.

Control flow: Xenbus creates a `xenvif`, later calls data/control connect helpers, and finally turns carrier on. Host-originated packets enter `ndo_start_xmit`, are mapped to a queue via hash or netdev queue selection, filtered by multicast control if enabled, timestamped, and appended to the guest RX queue before the RX kthread is kicked. Guest TX interrupts schedule NAPI, while guest RX interrupts wake the RX kthread. Close/disconnect reverses this by disabling IRQs/NAPI, stopping kthreads, unmapping rings, freeing multicast state, and dropping carrier.

State and persistence behavior: State is in memory only: VIF feature flags, queue pointers, per-queue grant page pools, pending rings, interrupt numbers, RX/TX SKB queues, kthread handles, inflight zerocopy counters, credit timers, status bits, hash/multicast state, and aggregate stats. There is no persistent storage; XenStore negotiation reconstructs everything on reconnect.

Dependencies and integration points: The file depends on Linux netdev, NAPI, ethtool, RCU, kthreads, grant tables, Xen event channels with late EOI, Xenbus ring mapping, and helper APIs implemented in `netback.c`, `rx.c`, and hash/control code.

Risks: The main risks are lifecycle races between IRQ handlers, NAPI, kthreads, and disconnect; queue selection when `num_queues` changes under RCU; grant page leaks on partial setup failures; and zerocopy inflight accounting that must wake the deallocation thread after each completion. Event-channel EOI flags must be cleared exactly when no work is pending.

Test signals: Exercise hotplug/probe/remove, open/close, split and shared event channels, multi-queue queue selection, carrier transitions, multicast filtering, RX queue overflow/drop, kthread teardown with inflight zerocopy SKBs, ethtool stats aggregation, and reconnect paths after frontend or backend restart.
