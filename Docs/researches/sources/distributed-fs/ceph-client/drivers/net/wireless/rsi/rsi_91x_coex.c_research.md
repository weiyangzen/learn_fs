# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_coex.c

Purpose: WLAN/Bluetooth coexistence queueing for RSI 91x devices.

Important APIs/functions: `rsi_coex_attach()` allocates the coexistence control block, initializes common/WLAN/BT queues, and starts a scheduler kthread. `rsi_coex_detach()` stops the thread, purges queues, and frees state. `rsi_coex_send_pkt()` maps HAL queues and dispatches WLAN/common packets or enqueues BT packets. `rsi_coex_recv_pkt()` handles common card-ready and sleep-notify indications.

Control flow: outbound packets are mapped from HAL queue IDs to coexistence queues. Common/WLAN packets are normally sent immediately via management/data paths; BT packets are queued and wake the coex TX thread. The scheduler repeatedly picks the last non-empty priority among common, BT, and WLAN, but only actively dequeues/sends BT packets in this file.

State and persistence: `struct rsi_coex_ctrl_block` holds queues, private common pointer, and thread event/completion state. It persists while the common driver instance is attached.

Dependencies/integration: RSI common state, HAL send functions, management handling, BT packet sender, and driver thread/event helpers. It is built only with `CONFIG_RSI_COEX`.

Risks: queue priority selection overwrites earlier choices, effectively preferring WLAN over BT over common for detection; the scheduler only services BT, so common/WLAN are handled through direct paths. Interface-down handling drops non-internal management packets with TX status.

Test signals: coex attach/detach, BT packet transmission, common card-ready handling, interface-down packet drops, and queue purging on module unload.
