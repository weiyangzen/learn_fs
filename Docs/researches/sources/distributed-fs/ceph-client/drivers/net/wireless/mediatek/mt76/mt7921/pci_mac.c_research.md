# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mac.c

## Purpose
This file contains PCIe-specific TX preparation and MAC reset recovery for MT7921. It handles TXWI/HW TXP creation for DMA tokens and performs a full PCI/WPDMA-oriented firmware/MAC restart after reset.

## Important APIs, Types, And Functions
`mt7921e_tx_prepare_skb()` is the PCI driver-op TX prepare callback. It allocates a mt76 token, requests periodic TX status for stations, writes the connac2 TXWI, writes the hardware TXP descriptor, and hands SKB ownership to DMA. `mt7921e_mac_reset()` is the PCI HIF reset callback used by reset work.

## Control Flow
TX prepare rejects too-short frames, defaults missing WCID to global WCID, stores the SKB in the TXWI cache area, consumes a token, optionally requests status once per station per quarter-second, allocates a packet-status id, writes TXWI and HW TXP, and nulls `tx_info->skb` so the caller knows DMA owns it.

Reset takes driver ownership, frees pending TX, disables host and PCI MAC interrupts, marks MCU reset, wakes MCU waiters, purges responses, schedules TX queues, disables TX worker and NAPI, frees tokens, resets the token idr, resets WPDMA, re-enables RX NAPI, clears firmware assert/MCU reset, restores interrupts, takes driver ownership again, runs firmware, sets EEPROM, initializes MAC, starts the PHY, and finally re-enables TX NAPI and TX worker.

## State And Persistence
TX state includes mt76 tokens, packet ids, TXWI cache entries, station `last_txs`, and DMA descriptors. Reset state includes interrupt masks, NAPI enablement, worker state, MCU reset bit, response queue, token idr, `fw_assert`, firmware running state, EEPROM/MAC state, and running PHY state.

## Dependencies And Integration Points
It depends on mt76 DMA/token helpers, connac2 TXWI/TXP helpers, PCI interrupt registers from `regs.h`, firmware and MAC init from common code, and HIF ownership helpers from `pci_mcu.c`/mt792x.

## Risks
Token ownership is delicate: failures after token consume must be unwound by later layers or avoided. Reset temporarily disables many asynchronous paths and must re-enable NAPI/workers even when firmware init fails. Reinitializing the token idr while SKBs are still referenced would corrupt completions, hence pending TX cleanup comes first. Interrupt masks must match the PCI probe IRQ map, including MT7902 differences.

## Test Signals
Transmit on all ACs, management frames, encrypted frames, aggregation setup, status reporting cadence, token exhaustion, and reset under traffic. After reset, firmware should rerun, MAC init should succeed, queues should wake, and TX/RX should resume without token leaks or stuck NAPI.
