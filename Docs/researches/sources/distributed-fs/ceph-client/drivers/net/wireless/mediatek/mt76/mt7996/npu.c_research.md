# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/npu.c

## Purpose
`npu.c` implements optional Airoha NPU offload setup and teardown for MT7996-family WLAN devices. It programs the NPU with WLAN PCIe register addresses, descriptor counts, token sizing, RX/TX descriptor bases, TX buffer-space DMA bases, TX-done event rings, and interrupt enablement so selected traffic/RRO paths can be offloaded from host processing.

## Important APIs, Types, And Functions
The chip-specific TX/RX setup functions are `mt7996_npu_txrx_offload_init()` and `mt7992_npu_txrx_offload_init()`. `mt7996_npu_offload_init()` reads the NPU firmware version, configures PCIe port type, delegates chip-specific ring setup, sets token ID size, and updates `dev->mt76.token_start`. RX descriptor base functions are split as `mt7996_npu_rxd_init()` and `mt7992_npu_rxd_init()`. `mt7996_npu_txd_init()` retrieves NPU TX ring descriptor bases and sends per-band TX buffer-space base addresses from `dev->npu_txd_addr`.

Additional setup helpers configure TX-done event handling (`mt7996_npu_rx_event_init()`), RRO RX PCIe addresses (`mt7996_npu_set_pcie_addr()`), and TX-done/reset inode addresses (`mt7996_npu_tx_done_init()`). Exported entry points are `mt7996_npu_rx_queues_init()`, `__mt7996_npu_hw_init()`, `mt7996_npu_hw_init()`, and `mt7996_npu_hw_stop()`.

## Control Flow
`mt7996_npu_hw_init()` first allocates coherent DMA memory for groups of three TX descriptor/buffer regions per offloaded band and records the DMA addresses in `dev->npu_txd_addr`. Under `dev->mt76.mutex`, `__mt7996_npu_hw_init()` obtains the RCU-protected `airoha_npu`, initializes offload parameters, writes RX descriptor bases into mt76 queue register blocks, writes TX descriptor bases into per-phy TX queues, configures TX-done and PCIe addresses, then enables two NPU WLAN IRQs.

`mt7996_npu_rx_queues_init()` initializes mt76 NPU RX queues only when an NPU device is active. Stop flow locks the mt76 mutex, disables a TX/RX inode address, polls NPU info up to ten times waiting for quiescence, then clears a second inode address; failure logs `npu stop failed`.

## State And Persistence
NPU setup mutates `dev->npu_txd_addr[]`, mt76 RX/TX queue descriptor-base registers, `dev->mt76.token_start`, NPU firmware-side descriptor counts and PCIe addresses, and active NPU IRQ state. It uses DMA-coherent allocations owned by `dmam_alloc_coherent()`, so lifetime is device-managed rather than manually freed in this file. No persistent filesystem state is written.

## Dependencies And Integration Points
The file depends on `linux/soc/airoha/airoha_offload.h`, mt76 NPU helpers (`mt76_npu_send_msg`, `mt76_npu_get_msg`, `mt76_npu_rx_queue_init`, `mt76_npu_device_active`), MMIO physical base addresses from `dev->mt76.mmio`, queue/register constants from `regs.h` and `mt7996.h`, and device mutex/RCU synchronization from mt76. It is compiled only when enabled by `CONFIG_MT7996_NPU`; otherwise `mt7996.h` supplies no-op stubs.

## Risks
The code is highly dependent on magic NPU function IDs, ring IDs, and per-chip queue mappings. Incorrect offsets or band-to-phy mapping can point the NPU at the wrong WFDMA ring. DMA allocation sizes differ between MT7996 and MT7992 paths and must match NPU firmware expectations. `writel()` updates queue descriptor bases directly, so calling order relative to mt76 DMA setup matters. Stop polling has a bounded timeout and may leave offload partially enabled on failure.

## Test Signals
Important signals are NPU firmware version logs, successful `mt76_npu_send_msg()`/`get_msg()` calls, initialized `MT_RXQ_NPU0/1`, valid descriptor-base writes for RRO/MSDU/IND/TX rings, traffic through NPU offload without RX/TX stalls, correct behavior on MT7996 versus MT7992 mappings, clean stop without timeout, and recovery after reset or NPU absence.
