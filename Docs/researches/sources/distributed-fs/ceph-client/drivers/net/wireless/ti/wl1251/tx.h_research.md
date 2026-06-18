# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/tx.h

Purpose: Defines wl1251 TX descriptor/control/result layouts, status bits, alignment helpers, queue mapping, and TX path entry points.

Important APIs and types: `struct tx_control`, `struct tx_double_buffer_desc`, `struct tx_result`, TX status bit enum, `wl1251_tx_get_queue()`, `wl1251_tx_work()`, `wl1251_tx_complete()`, and `wl1251_tx_flush()`.

Control flow: Header comments document host TX double-buffer flow and TX-complete cyclic ring ownership protocol. `wl1251_tx_get_queue()` maps mac80211 queue indexes to firmware AC queues VO/VI/BE/BK.

State and persistence: No stored state in the header; packed structures define firmware-owned/shared memory layouts and host-owned SKB metadata IDs.

Dependencies and integration points: Included by `tx.c` and `main.c`; descriptor size is used as mac80211 `extra_tx_headroom`.

Risks: Packed bitfields and firmware descriptors must match target ABI. Compiler bitfield layout assumptions are always a portability risk in hardware descriptors. Queue mapping must stay consistent with ACX queue config.

Test signals: Compile layout, successful TX completion ownership handoff, correct ACK status reporting, and queue mapping behavior under QoS traffic.
