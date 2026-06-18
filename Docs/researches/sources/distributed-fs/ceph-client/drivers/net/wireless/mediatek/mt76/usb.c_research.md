# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb.c

## Purpose
Provides the shared mt76 USB bus implementation: vendor control requests, register access, bulk RX/TX URB management, optional scatter-gather RX/TX, queue allocation, TX status workers, stop/resume/deinit helpers, and USB bus ops registration.

## Important APIs, Types, And Functions
Exports vendor/register helpers (`__mt76u_vendor_request()`, `mt76u_vendor_request()`, `___mt76u_rr()`, `___mt76u_wr()`, `mt76u_read_copy()`, `mt76u_single_wr()`), queue APIs (`mt76u_alloc_queues()`, `mt76u_alloc_mcu_queue()`, `mt76u_stop_rx()`, `mt76u_resume_rx()`, `mt76u_stop_tx()`, `mt76u_queues_deinit()`), and init APIs (`__mt76u_init()`, `mt76u_init()`). Queue ops are `mt76u_tx_queue_skb()` and `mt76u_tx_kick()`.

## Control Flow
Register access serializes through `usb_ctrl_mtx` and retries vendor control messages, marking the device removed on ENODEV/EPROTO. Init allocates the control buffer, sets bus/queue ops, records USB drvdata, detects scatter-gather support, discovers endpoints, and starts RX/status workers. RX URBs complete into queue entries, schedule `rx_worker`, are parsed into SKBs/frags, passed to `drv->rx_skb()`, refilled, and resubmitted. TX prepares SKBs, fills bulk URBs, submits pending URBs, completes via status worker, and optionally polls firmware TX status data.

## State And Persistence
State lives in `dev->usb`: endpoint arrays, control buffer, mutex, SG enable, RX/status workers, stat work, and URBs stored in queue entries. Queue state tracks `head`, `tail`, `first`, `queued`, `done`, endpoint mapping, and page-pool buffers. Module parameter `disable_usb_sg` persistently controls SG use.

## Dependencies And Integration Points
Depends on Linux USB core, page_pool, scatterlist helpers, mt76 worker and queue APIs, mt76 DMA header constants, driver callbacks `tx_prepare_skb()`, `rx_skb()`, `rx_check()`, and `tx_status_data()`, plus USB tracepoints.

## Risks
URB ownership and page-pool recycling are delicate, especially with SG RX where an SKB may own multiple pages. Stop paths must poison/kill URBs and manually complete queued SKBs after removal. Vendor requests log writes even for some non-register control operations. Endpoint mapping has chip-specific cases; wrong mapping can route PSD/AC traffic incorrectly.

## Test Signals
Probe on supported USB chips, SG enabled/disabled operation, RX aggregation and fragmented SKBs, TX queue drain, MCU RX queue allocation, suspend/resume RX, removal during TX submission, vendor request timeout handling, and visible `mt76_usb` trace events.
