# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-imx-lpi2c.c

Purpose: NXP/Freescale i.MX LPI2C adapter driver. It supports master transfers through PIO, atomic PIO, or DMA, SMBus block read, optional target/slave mode, bus recovery pinctrl integration, runtime/system PM, SoC-specific clock/IRQ handling, and multiple speed modes up to ultra-fast.

Important APIs/types/functions: `struct lpi2c_imx_struct` owns adapter, clocks, MMIO, transfer buffers/completion, bitrate/FIFO sizes, recovery info, DMA state, optional target client, IRQ, and SoC hwdata. `struct lpi2c_imx_dma` tracks DMA channels, buffers, burst sizing, mappings, and fallback state. Key functions are `lpi2c_imx_config()`, master enable/disable, start/stop, PIO read/write helpers, DMA setup/submit/cleanup, `lpi2c_imx_xfer_common()`, master/target ISRs, target register/unregister, DMA init/exit, probe/remove, and PM callbacks.

Control flow: probe maps resources, gets clocks, reads bitrate, requests IRQ, enables runtime PM, reads FIFO sizes, initializes optional recovery and DMA, then registers the adapter. Transfers enable the master and runtime-resume, issue START for each message, skip payload for SMBus Quick, choose DMA for sufficiently large non-block-read messages when not suspending, otherwise use PIO, wait for completion/polling, wait for TX FIFO empty on writes, issue STOP, check NACK, and disable the master. DMA RX uses both TX DMA for receive-command words and RX DMA for data.

State and persistence: active state includes RX/TX buffers, delivered count, message length, SMBus block flag, completion, DMA mappings, and target pointer. Persistent configuration includes bitrate mode, clock rate, FIFO sizes, recovery info, DMA availability, and SoC hwdata flags. Runtime suspend may free IRQ and disable/unprepare clocks on selected SoCs; resume restores pinctrl/clocks/IRQ. Target mode is reinitialized after noirq resume.

Dependencies and integration: depends on OF match data for imx7ulp/imx8qxp/imx8qm, clock bulk APIs, DMAengine, runtime PM, pinctrl bus recovery, I2C master/target APIs, completions, and MMIO polling helpers.

Risks: DMA has many failure points and only falls back to PIO before DMA actually starts. SMBus block read mutates message length after reading the length byte and must avoid premature controller NACK. `pm_runtime_get_sync()` style paths in related code are avoided here mostly, but PM sequencing is intricate. Target mode shares the IRQ with master mode. Some SoCs free/re-request IRQ during runtime PM, increasing resume failure surface.

Test signals: PIO and DMA read/write thresholds, DMA fallback before start, long RX requiring multiple command words, SMBus block read length validation, atomic transfers during atomic contexts, NACK/arbitration/timeout recovery, target read/write/stop callbacks, bus recovery pinctrl, runtime suspend/resume with IRQ re-request SoCs, and system suspend/resume target reinit.
