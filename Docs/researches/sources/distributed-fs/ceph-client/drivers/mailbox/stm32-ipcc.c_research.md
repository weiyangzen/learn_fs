# sources/distributed-fs/ceph-client/drivers/mailbox/stm32-ipcc.c

Purpose: implements the STM32MP1 IPCC mailbox controller for two processors, exposing hardware channels where TX sets a channel occupied bit and RX observes the other processor's occupied state.

Important APIs/types/functions: `struct stm32_ipcc` stores controller, base/proc register pointers, clock, lock, IRQs, processor id, channel count, and suspend register context. Ops are `stm32_ipcc_send_data`, startup, and shutdown. IRQ handlers `stm32_ipcc_rx_irq` and `stm32_ipcc_tx_irq` deliver RX events and txdone.

Control flow: probe reads `st,proc-id`, maps registers, enables the clock, requests threaded RX/TX IRQs, masks all channel IRQs, enables RX/TX output interrupt generation, configures optional wake IRQ, reads hardware channel count, initializes channel ids, registers a txdone-IRQ controller, logs version, and disables the clock until channel startup. Startup enables the clock and unmasks RX occupied IRQ for the channel. Send sets the TX occupied bit and unmasks TX-free IRQ. RX IRQ finds unmasked occupied channels from the other processor, calls `mbox_chan_received_data(chan, NULL)`, then sets the RX clear bit. TX IRQ finds unmasked free channels, masks the TX-free interrupt, and calls `mbox_chan_txdone`.

State and persistence: channel masks and control registers are hardware state; suspend stores/restores `XMR` and `XCR`. Clock is enabled per active channel but without a refcount in this driver.

Dependencies and integration: depends on STM32 DT compatible, `st,proc-id`, RX/TX named IRQs, clock, wakeirq support, and mailbox framework.

Risks: multiple simultaneous channel users call `clk_prepare_enable`/`clk_disable_unprepare` independently without explicit refcounting in driver code. RX carries no payload, so protocol state lives in clients/shared memory.

Test signals: proc-id validation, RX/TX IRQ behavior per channel, wakeup-source suspend/resume, channel count from HWCFGR, and multi-channel clock lifecycle.
