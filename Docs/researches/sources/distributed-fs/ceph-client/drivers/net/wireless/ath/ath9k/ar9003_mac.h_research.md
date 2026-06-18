# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9003_mac.h

Purpose: Defines AR9003 MAC descriptor layouts and bit masks used by the AR9003 EDMA TX/RX implementation, and declares the MAC operation attach and EDMA helper APIs.

Important APIs and types: Descriptor identity and control masks include `AR_DescId`, `AR_CtrlStat`, `AR_TxRxDesc`, `AR_TxQcuNum`, `AR_BufLen`, `AR_TxDescId`, `AR_TxPtrChkSum`, `AR_LowRxChain`, `AR_Not_Sounding`, and `AR_PAPRDChainMask`. ISR secondary-bit mapping constants translate AR_ISR_S2 bits into ath9k interrupt bits. `struct ar9003_rxs` describes 12 dwords of RX status, `struct ar9003_txc` describes the 128-byte TX control descriptor with four data pointers and control words `ctl3` through `ctl23`, and `struct ar9003_txs` describes TX status-ring entries. Prototypes expose `ar9003_hw_attach_mac_ops()`, RX buffer-size/RXDP programming, EDMA RX status processing, and TX status-ring setup/reset.

Control flow: The header has no executable flow. Its structs are filled and consumed by `ar9003_mac.c`: TX setup writes `ar9003_txc`, hardware writes `ar9003_txs` and `ar9003_rxs`, and descriptor/status fields are decoded through the masks defined here.

State and persistence: No owned state. The packed, 4-byte-aligned structs define DMA-visible in-memory state shared between driver and hardware. The 128-byte TX control descriptor padding is intentional cache-line sizing.

Dependencies and integration points: Included by `ar9003_mac.c` and `ar9003_hw.c`, and indirectly tied to common ath9k types from `hw.h` such as `struct ath_hw`, `struct ath_rx_status`, and `enum ath9k_rx_qtype`. The bit definitions complement register/status field macros from shared ath9k hardware headers.

Risks: Layout, packing, alignment, and bit positions are hardware ABI. Changing `struct ar9003_txc` size, removing padding, or altering status dword order would corrupt DMA. `AR9003TXC_CONST()` is a raw cast helper, so callers must pass a true AR9003 TX descriptor. ISR map constants encode shifts in both directions and are easy to misuse if AR_ISR_S2 definitions change.

Test signals: Compile-time size/alignment checks for descriptor structs, TX/RX DMA tests on EDMA hardware, descriptor checksum verification, interrupt decode tests for beacon misc bits, and sparse/static analysis for casts through `AR9003TXC_CONST()`.
