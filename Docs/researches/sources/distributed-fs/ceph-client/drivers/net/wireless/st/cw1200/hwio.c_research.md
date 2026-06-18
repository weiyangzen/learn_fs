# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/hwio.c

Purpose: Low-level register, data queue, APB, and AHB accessors for CW1200 hardware through `hwbus_ops`.

Important APIs and functions: Public functions are `cw1200_reg_read`, `cw1200_reg_write`, `cw1200_data_read`, `cw1200_data_write`, `cw1200_indirect_read`, `cw1200_apb_write`, and `__cw1200_irq_enable`. Internal helpers implement raw register reads/writes with SDIO-style 17-bit address formation and endian conversion.

Control flow: Register accessors lock the bus, perform one raw transfer, and unlock. Data read/write uses the queue register with rotating RX/TX buffer IDs and retries up to three times. Indirect reads write the SRAM base address, set a prefetch bit, poll for prefetch completion, then read the data port. APB writes set the base address and write the SRAM data port. IRQ enable manipulates different config bits depending on hardware type.

State and persistence: Updates `priv->buf_id_rx` and `priv->buf_id_tx`; otherwise performs hardware register state changes. IRQ enable writes persist in device registers until changed.

Dependencies and integration: Depends on `hwbus_ops` implementations, register constants from `hwio.h`, `cw1200_common` hardware type, and callers in firmware loading and BH paths.

Risks: Buffer alignment is enforced for reads larger than four bytes. Retry loops use blocking delays. `cw1200_data_read/write` return the last `ret`, so retry exhaustion behavior must be monitored. Indirect access limits transfers to less than 0x1000 words. IRQ enable must be called with bus lock when using `__cw1200_irq_enable`.

Test signals: Register read/write loopback where possible, firmware APB writes, AHB cut-ID reads, data queue transfers with retry injection, buffer-ID rollover, and IRQ bit toggling on both supported hardware paths.
