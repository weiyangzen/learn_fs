# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_sdio.h

Purpose: Defines the RSI SDIO transport ABI, interrupt status decoding, device-private state, and SDIO helper prototypes.

Important APIs and types: `enum sdio_interrupt_type` maps firmware/SDIO interrupt causes to buffer availability, firmware assert, MSDU pending, and unknown status. Register constants identify function registers, firmware status, read/write FIFO controls, master access windows, wakeup register, interrupt clear, high-speed mode, and TA reset/hold/release addresses. `RSI_GET_SDIO_INTERRUPT_TYPE()` derives a typed interrupt from raw status bits. `struct receive_info` accumulates buffer-full/semi-full/management-full flags and interrupt counters. `struct rsi_91x_sdiodev` stores the SDIO function, IRQ/RX thread state, block size, previous descriptor, buffer status, aligned packet buffer, and write failure flag.

Control flow and integration: The SDIO implementation uses this header to initialize slave registers, read/write single or multiple registers, switch master access high words, acknowledge interrupts, determine event timeouts, check firmware buffer status before TX, and run `rsi_sdio_rx_thread()` to fetch pending frames.

State and persistence: Persistent transport state includes current buffer-full status, next read delay, high-speed/clock settings, card capability, TX block size, previous descriptor cache, and interrupt counters. Firmware-visible state lives in the function registers and TA control registers.

Dependencies: Depends on Linux MMC/SDIO APIs and RSI core types from `rsi_main.h`. It is coupled to RSI queue status behavior and firmware interrupt bit assignments.

Risks and test signals: Risks include stale buffer-status flags blocking TX, incorrect interrupt classification, unacknowledged function interrupts, master-access window mistakes for high addresses, and DMA/alignment assumptions for `pktbuffer`. Tests should cover interrupt status decoding, buffer full/semi-full recovery, firmware assert indication, register multi-write/read alignment, high-speed enablement, RX pending handling, and queue status timeouts.

Test signals: Source read size: 138 lines, 4842 bytes.
