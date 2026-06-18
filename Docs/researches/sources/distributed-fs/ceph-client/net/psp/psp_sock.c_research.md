# sources/distributed-fs/ceph-client/net/psp/psp_sock.c

## Purpose
`psp_sock.c` binds PSP security associations to TCP sockets and time-wait sockets. It provides association allocation/lifetime management, route-device discovery, RX/TX association installation, transmit validation, key-rotation stale handling, and a helper to mark replies decrypted.

## Important APIs, Types, And Functions
Important exported or cross-file functions are `psp_dev_get_for_sock()`, `psp_assoc_create()`, `psp_dev_tx_key_del()`, `psp_assoc_put()`, `psp_sk_assoc_free()`, `psp_sock_assoc_set_rx()`, `psp_sock_assoc_set_tx()`, `psp_assocs_key_rotated()`, `psp_twsk_init()`, `psp_twsk_assoc_free()`, and `psp_reply_set_decrypted()`. Internal helpers include `psp_validate_xmit()`, `psp_assoc_dummy()`, `psp_dev_tx_key_add()`, `psp_assoc_free_queue()`, and `psp_sock_recv_queue_check()`.

## Control Flow
`psp_dev_get_for_sock()` uses RCU to inspect the socket destination cache, read the netdevice's PSP device, and take a weak device ref. Association creation requires the PSP device lock, allocates a flexible structure sized for driver private association data, snapshots device id and generation, takes a device ref, initializes the association refcount, and links it into the device active list.

RX setup copies the allocated key into `pas->rx`, locks the socket, rejects sockets with existing PSP state, takes another association ref, and publishes `sk->psp_assoc` with RCU assignment. TX setup requires an existing RX association on the same device/version and no existing TX SPI. It scans TCP out-of-order and receive queues for PSP skb extensions that do not match the association, creates a dummy association for the driver `tx_key_add()` callback, copies driver private data and TX key into the real association, installs `psp_validate_xmit`, fences TCP write collapse, records the upgrade sequence, and increases TCP external header length before recomputing MSS.

Freeing is RCU-delayed and then workqueue-based because driver key deletion takes the PSP device mutex. Time-wait initialization copies the association ref to the time-wait socket and installs transmit validation. Key rotation moves active associations to previous, previous to stale, and poisons old generations so RX can reject stale traffic.

## State And Persistence
State is in `sk->psp_assoc`, `tw->psp_assoc`, association refcounts, per-device active/previous/stale lists, association generation, driver private data, and TCP socket header/MSS fields. It is volatile and tied to socket/device lifetimes.

## Dependencies And Integration Points
The file integrates with TCP internals (`tcp_sk`, receive queues, out-of-order rb tree, MSS sync), skb extensions (`SKB_EXT_PSP`), destination/netdevice PSP pointers, driver TX key callbacks, and RCU/workqueue lifetime rules. `psp_nl.c` drives RX/TX setup through this file.

## Risks
The TX path must avoid attaching TX keys if any queued received segments belong to different PSP state; otherwise data may be misclassified. The dummy association is a deliberate guard against drivers keeping transient pointers. Lifetime spans RCU and workqueue contexts, so association list deletion and device op availability (`psd->ops`) are sensitive during unregister. TCP header-length mutation must stay paired with PSP overhead semantics.

## Test Signals
Tests should cover duplicate RX/TX setup rejection, device/version mismatch, queued incompatible skb extensions, driver `tx_key_add()` failure, association release after socket close and time-wait conversion, key-rotation list movement/stale stats, and transmit validation dropping skbs whose association device differs from the egress netdevice.
