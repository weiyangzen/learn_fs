# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac.h

Purpose: Shared Connac-family declarations for packet types, descriptor sizes, chip predicates, PM/coredump state, TXP layouts, inline helpers, and exported MAC/PM utility prototypes used by mt7615 and newer MediaTek chips.

Important APIs and types: `enum rx_pkt_type` classifies RX packet/event types. `struct mt76_connac_pm` stores power-save enable flags, wake refs, queued skbs, work items, waitqueue, mutex, idle timeout, and PM statistics. `struct mt76_connac_coredump` buffers firmware crash messages. `struct mt76_connac_fw_txp`, `struct mt76_connac_hw_txp`, and `struct mt76_connac_txp_common` define firmware and hardware TX pointer descriptors. Chip helpers such as `is_mt7615()`, `is_mt7663()`, `is_connac_v1()`, `is_connac2()`, and `is_mt799x()` drive variant behavior. Inline helpers map channel width, AC queues, TXWI to TXP, antenna masks to SPE index, IRQ reenablement, PM refs, skip-fw-PM decisions, and PM-aware mutex acquisition.

Control flow and integration: Drivers include this header to decide descriptor formats, PM transitions, and chip feature paths. mt7615 uses its PM mutex macros over `mt76_connac_mutex_acquire/release()`, TX paths call TXP helpers, interrupt code uses `mt76_connac_irq_enable()`, and USB/SDIO/PCI paths depend on chip predicates.

State and persistence: Defines host runtime PM, token/TXP, coredump, and pending TX state. Persistent firmware crash data may be buffered in memory for coredumps but not written here.

Dependencies: Core `mt76.h`, mac80211/nl80211 types, kernel workqueues/spinlocks/mutexes, and descriptor bit macros from companion MAC headers.

Risks: Chip predicate mistakes route devices through wrong descriptor, PM, or register paths. PM ref accounting must stay balanced; underflow or skipped unref can prevent sleep or allow sleep with active traffic. TXP layouts are DMA ABI and must match unmap logic. `mt76_connac_irq_enable()` schedules tasklets after mask changes, which assumes caller context can tolerate immediate bottom-half work.

Test signals: Build coverage across Connac drivers, PM wake/sleep stats, TX completion/unmap correctness, chip-specific feature selection, coredump collection, and packet flow on all supported buses.
