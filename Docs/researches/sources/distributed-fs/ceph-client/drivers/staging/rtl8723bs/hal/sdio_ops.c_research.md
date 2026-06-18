# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/sdio_ops.c

Purpose: this file implements RTL8723BS SDIO address translation, register/memory/port IO operations, SDIO local register access, interrupt handling, RX FIFO draining, and TX buffer status queries.

Important APIs and functions: `sdio_set_intf_ops` installs `_read8/_read16/_read32/_read_mem/_read_port` and write counterparts. `_cvrt2ftaddr` and `hal_sdio_get_cmd_addr_8723b` map pseudo-addresses/device IDs to SDIO function-transfer addresses. `sdio_read_port` and `sdio_write_port` move RX/TX FIFO data. `EnableInterrupt8723BSdio`, `DisableInterrupt8723BSdio`, `sd_int_hdl`, and `sd_int_dpc` handle host interrupts. `HalQueryTxBufferStatus8723BSdio` and `HalQueryTxOQTBufferStatus8723BSdio` refresh transmit resource state.

Control flow: normal register access maps the address to a device ID and chooses CMD52 for early IO, low MAC power, or firmware power-save mode; otherwise CMD53/block access is used with alignment fixups. RX interrupts read `SDIO_REG_RX0_REQ_LEN`, pull RX FIFO data into a `recv_buf`, enqueue it, and schedule the receive tasklet until no more RX request is pending. AVAL interrupts refresh free pages and complete TX waiters; C2H interrupts read firmware events and either handle CCX directly or queue work; CPWM interrupts wake power-control work.

State and persistence: SDIO runtime state is in `hal_com_data.sdio_himr`, `sdio_hisr`, `SdioRxFIFOCnt`, `SdioRxFIFOSize`, `SdioTxFIFOFreePage`, and `SdioTxOQTFreeSpace`. `sdio_data.block_transfer_len` controls transfer rounding. Adapter hardware-init and power-save flags gate IO mode.

Dependencies and integration: depends on low-level SDIO helpers (`sd_read`, `_sd_read`, `sd_cmd52_read`, `sd_write`), receive buffers from `rtl8723bs_recv.c`, xmit completions from `rtl8723bs_xmit.c`, C2H handlers, and register definitions in `hal_com_reg.h`.

Risks and test signals: unaligned read/write paths allocate temporary buffers in atomic context and can fail. `sd_recv_rxfifo` returns `NULL` without requeueing if skb allocation or port read fails after a recvbuf is dequeued, so RX starvation paths need attention. Tests should cover early CMD52-only register access, CMD53 alignment, block-size rounding, interrupt clear masks, repeated RX packets in one interrupt, TX free-page completion, C2H queueing, CPWM power events, and surprise removal guards.
