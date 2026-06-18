# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/dma.c

Purpose: DMA and queue initialization/cleanup for MT7615 PCIe/MMIO-style devices and related MT7622/MT7663 variants.

Important APIs/functions: defines TX queue setup (`mt7615_init_tx_queues()`, `mt7622_init_tx_queues_multi()`), NAPI pollers (`mt7615_poll_rx()`, `mt7615_poll_tx()`), busy polling (`mt7615_wait_pdma_busy()`), DMA scheduler setup for MT7622/MT7663, `mt7615_dma_start()`, `mt7615_dma_init()`, and `mt7615_dma_cleanup()`.

Control flow: `mt7615_dma_init()` attaches mt76 DMA, programs WPDMA global flags and MT7615-specific prefetch/abort settings, resets ring indices, initializes firmware-download and WM MCU queues, initializes data/mgmt queues according to chip type, allocates MCU and main RX rings, installs RX/TX NAPI handlers, waits for idle DMA, enables TX/RX/MCU interrupts, then starts DMA and scheduler quotas. Pollers take runtime-PM references; if the chip is asleep they complete NAPI and queue wake work. Cleanup disables DMA, asserts software reset, and delegates ring cleanup to mt76.

State and persistence: initializes volatile DMA ring state, queue descriptors, interrupt masks, NAPI state, WPDMA configuration, and DMASHDL quotas. No disk persistence; ring contents and hardware queue state reset across device removal/reset.

Dependencies and integration: depends on mt76 DMA core (`../dma.h`), mt76 queue allocation helpers, connac runtime PM, chip tests (`is_mt7615`, `is_mt7622`, `is_mt7663`), and register definitions. Feeds RX packets into `mac.c` through mt76 queue plumbing.

Risks: queue IDs and ring sizes differ by chip; wrong mapping can starve AC/MCU queues. Runtime-PM reference failures must wake the device without losing NAPI progress. Busy polling timeouts indicate stuck PDMA/PSE and should block reset/start sequences. DMA scheduler quota values are hard-coded hardware tuning.

Test signals: successful probe with allocated TX/RX rings, interrupts for RX done and MCU TX done, no PDMA busy timeout, sustained traffic on all AC queues, firmware download through FWDL queue, and clean unload without DMA warnings.
