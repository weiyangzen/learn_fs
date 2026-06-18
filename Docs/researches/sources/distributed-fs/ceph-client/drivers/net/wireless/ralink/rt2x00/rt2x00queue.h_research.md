# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00queue.h

## Purpose
`rt2x00queue.h` defines the common queue data model and descriptor summary structures used by rt2x00 core, transports, and chip drivers. It gives all rt2x00 devices a shared vocabulary for queue IDs, skb driver metadata, RX/TX completion descriptors, TX descriptor intent, queue entries, queue indices, queue state flags, and queue iteration helpers.

## Important APIs, Types, And Functions
Important constants are `DATA_FRAME_SIZE`, `MGMT_FRAME_SIZE`, and `AGGREGATION_SIZE`. `enum data_queue_qid` maps mac80211 AC queues, management, RX, beacon, and ATIM queues. `struct skb_frame_desc` overlays mac80211 driver data and stores descriptor pointers, DMA address, IVs, TX rate reporting fields, and station pointer. `struct rxdone_entry_desc`, `struct txdone_entry_desc`, and `struct txentry_desc` are transport-neutral summaries consumed by rt2x00lib and chip drivers. `struct queue_entry` models one ring entry and `struct data_queue` models a whole queue. Inline helpers report empty/full/available/threshold status, descriptor word access, and DMA timeouts. Loop macros walk all queues or all TX queues.

## Control Flow
The header supports the queue lifecycle implemented in `rt2x00queue.c`: allocate `struct data_queue` objects, initialize each via chip `queue_init`, allocate entries with per-entry private transport data, map RX/TX skbs, and advance circular indices as hardware and software exchange ownership. `rt2x00queue_for_each_entry()` and the queue macros provide the traversal contract used by USB kicking/flushing and MMIO/chip completion paths.

## State And Persistence
Queue state is in memory only. `struct data_queue` tracks queue identity, flags, locks, count/limit/threshold/length, three circular indices, watchdog state, WMM parameters, frame and descriptor sizing, transport-specific USB endpoint metadata, and private-data size. `struct queue_entry` tracks per-slot flags, last action time, owning queue, skb, index, and transport private data. `struct skb_frame_desc` persists inside an skb while it is owned by rt2x00.

## Dependencies And Integration Points
This header integrates mac80211 metadata, Linux skb and DMA concepts, rate/cipher enums from `rt2x00reg.h`, queue users in `rt2x00queue.c`, transports in `rt2x00mmio.c` and `rt2x00usb.c`, and chip descriptor encoders such as `rt61pci_write_tx_desc()`. The descriptor read/write helpers centralize little-endian conversion for hardware descriptors.

## Risks
The skb descriptor has a build-time size assertion against `IEEE80211_TX_INFO_DRIVER_DATA_SIZE`; adding fields can break all builds. Queue index meanings must remain consistent across transports. Some macros do not bounds-check beyond their documented end pointers, so callers must choose the right range. Descriptor helpers assume little-endian descriptor words. `rt2x00queue_dma_timeout()` uses a fixed 100 ms timeout and only checks `ENTRY_OWNER_DEVICE_DATA`.

## Test Signals
Signals include compile-time size checks passing, queue allocation for drivers with and without ATIM, descriptor endian correctness in TX/RX status, queue threshold behavior, circular iteration over wraparound ranges, and successful use of the same queue structures by MMIO and USB transports.
