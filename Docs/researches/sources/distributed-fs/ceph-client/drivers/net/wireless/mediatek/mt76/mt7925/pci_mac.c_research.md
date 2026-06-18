# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/pci_mac.c

## Purpose
This file contains MT7925 PCIe MAC-side TX preparation and reset recovery. It builds PCIe TXWI/TXP descriptors, manages mt76 TX tokens, and reinitializes firmware, EEPROM, MAC, queues, interrupts, and runtime state after a PCIe MAC reset.

## Important APIs, Types, And Functions
`mt7925e_tx_prepare_skb()` is the PCIe `tx_prepare_skb` callback. `mt7925_tx_token_put()` frees all outstanding TXWI token cache entries. `mt7925e_mac_reset()` is the PCIe HIF reset callback used through `struct mt792x_hif_ops`.

## Control Flow
TX preparation validates packet length, falls back to the global WCID when needed, stores the SKB in a TXWI cache object, consumes an mt76 token, periodically requests TX status for stations, registers the SKB for TX status, writes an MT7925 TXWI, zeroes and fills the hardware TXP descriptor, and transfers SKB ownership to the queue. Reset takes driver PM ownership, frees pending TX SKBs, disables interrupts, sets reset bits, wakes MCU waiters, purges MCU responses, disables workers/NAPI, frees tokens, resets WPDMA, reenables NAPI and schedules RX/TX polling, clears firmware assertion state, reenables interrupts, reacquires firmware/driver ownership, reruns firmware, reapplies EEPROM, initializes MAC, and starts the PHY.

## State And Persistence
Token state lives in `dev->mt76.token`, `token_count`, and TXWI cache entries. Reset mutates `MT76_RESET`, `MT76_MCU_RESET`, `fw_assert`, TX worker state, NAPI state, MCU response queues, and hardware interrupt registers. Firmware, EEPROM, and MAC state are reloaded rather than preserved in place.

## Dependencies And Integration Points
The file depends on mt76 token/status infrastructure, `mt7925_mac_write_txwi()`, `mt76_connac_write_hw_txp()`, common WPDMA reset code, MT7925 firmware and EEPROM setters, MAC init, and the shared MT792x PM ownership functions. It is selected by PCI probe through `mt76_driver_ops`.

## Risks
Token leaks or double-frees can corrupt TX completion. Reset ordering is high risk: interrupts and NAPI must be quiesced before token destruction and reenabled only after WPDMA is valid. Firmware rerun failure paths must still clear reset state and reenable TX worker only when safe. Periodic TX status requests depend on per-station `last_txs` timing.

## Test Signals
Heavy TX, management TX, TX status reporting, firmware assert/reset, queue cleanup, IDR token consistency, NAPI disable/enable lockdep checks, and recovery into a working association validate this file.
