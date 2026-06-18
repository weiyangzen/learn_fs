# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/sdio.h

Purpose: Defines SDIO mailbox constants, CCCR bit definitions, RX bundle limits, sleep-control constants, and private SDIO transport state used by `sdio.c`.

Important APIs and types: Exposes `ATH10K_HIF_MBOX_*`, `ATH10K_SDIO_MAX_BUFFER_SIZE`, `ATH10K_HTC_MBOX_MAX_PAYLOAD_LENGTH`, `ATH10K_SDIO_MAX_RX_MSGS`, sleep/RTC constants, `enum sdio_mbox_state`, `ath10k_sdio_bus_request`, `ath10k_sdio_rx_data`, IRQ register shadow structures, mailbox geometry structures, `struct ath10k_sdio`, and `ath10k_sdio_priv()`.

Control flow, state, and persistence: The header owns no flow, but its structures define the state machine used by SDIO HIF: request allocation/free queues, asynchronous write work, RX packet staging, IRQ shadow protection, mailbox swap metadata, VSG/BMI temporary buffers, disabled state, and sleep timer state.

Dependencies and integration points: Depends on Linux SDIO definitions and ath10k HTC endpoint IDs. It is consumed by `sdio.c` and indirectly by ath10k core/HIF code through `ar->drv_priv`.

Risks: Buffer-size constants bound both allocation and validation, so mismatches can truncate HTC payloads or overrun VSG bundle buffers. The `TODO` about replacing bus requests with `skb->cb` highlights lifetime/ownership complexity. Mutex/spinlock comments are part of the concurrency contract because SDIO memory copies can sleep.

Test signals: Compile SDIO builds, validate maximum HTC payload, RX bundle counts, mailbox address calculation, sleep state transitions, and interrupt register shadow writes under lockdep.
