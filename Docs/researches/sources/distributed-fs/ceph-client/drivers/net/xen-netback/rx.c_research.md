# sources/distributed-fs/ceph-client/drivers/net/xen-netback/rx.c

Purpose: Implements the backend-to-frontend receive path: packets queued by the backend netdev are copied into guest-provided RX grant slots, decorated with Xen extra-info records for GSO/XDP/hash, and completed through the frontend RX ring.

Important APIs, types, and functions: `xenvif_rx_queue_tail()` enqueues host SKBs and manages internal byte limits; `xenvif_kthread_guest_rx()` is the per-queue RX worker; `xenvif_rx_action()` drains queued SKBs while frontend slots are available; `xenvif_rx_skb()` writes data and extra slots for one packet; `xenvif_rx_copy_add()` and `xenvif_rx_copy_flush()` batch grant copies; `xenvif_have_rx_work()` drives IRQ/kthread wake logic and stall detection.

Control flow: `xenvif_start_xmit()` queues an SKB with an expiry deadline, then wakes the RX kthread. The worker waits for either sufficient RX ring slots, stall/ready transitions, stop requests, or disabled VIF state. For each packet, it computes required slots, dequeues the SKB, builds extra-info records for supported GSO, XDP headroom, and software hash, copies packet chunks into guest grants without crossing guest or source pages, writes RX responses, pushes notifications, and frees completed SKBs.

State and persistence behavior: Queue state includes the internal SKB queue, `rx_queue_len`, byte limit, `rx_slots_needed`, `last_rx_time`, `stalled`, batched grant-copy arrays, and completed SKB list. VIF-wide stall counters gate netdev carrier. All state is volatile and tied to live rings and kthreads.

Dependencies and integration points: Relies on Xen RX ring macros, grant-table copy operations, netdev queue stop/wake, SKB frag traversal, GSO/hash metadata, XDP headroom negotiated by Xenbus, and event-channel late EOI handling shared with `interface.c`.

Risks: Incorrect slot accounting can overrun frontend rings or sleep forever waiting for unavailable slots. Queued SKBs may hold foreign pages, so expiry/drop handling prevents grant starvation. Stall detection affects carrier state across all queues. Copy batching must update response status if individual grant copies fail.

Test signals: Cover packets spanning pages/frags/frag_lists, GSO extra-info, XDP headroom extra-info, hash extra-info, small and full RX rings, queue byte-limit backpressure, packet expiry, guest RX stall and recovery, grant-copy failures, split/shared IRQ EOI behavior, and kthread stop while disabled.
