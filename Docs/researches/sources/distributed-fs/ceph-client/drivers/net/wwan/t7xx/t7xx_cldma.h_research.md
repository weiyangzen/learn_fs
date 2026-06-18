# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_cldma.h

Purpose: defines CLDMA hardware constants, register offsets, interrupt masks, reset bits, queue counts, hardware mode enums, and public low-level CLDMA operations.

Important APIs/types: `CLDMA_TXQ_NUM`/`CLDMA_RXQ_NUM` define eight TX and RX queues. Interrupt masks distinguish TX/RX done bits, empty queue bits, TX/RX error bits, and active-start errors. Register macros cover CLDMA0/1 AO/PD bases, UL/DL start/current/status/control registers, L2/L3 interrupt registers, busy masks, and infra reset bits. `enum mtk_txrx` identifies TX vs RX, `enum t7xx_hw_mode` captures DMA address width, and `struct t7xx_cldma_hw` stores mode, mapped bases, and interrupt ID.

Control flow and state: this header is the register contract consumed by `t7xx_cldma.c` and higher CLDMA HIF code. Queue operations are expressed by queue number or `CLDMA_ALL_Q`.

Dependencies and integration points: depends on Linux bit macros and types. It is included by `t7xx_hif_cldma.h` and low-level CLDMA implementation.

Risks and test signals: register definitions are hardware ABI. Wrong masks or offsets cause hard-to-debug interrupt storms, stalled queues, or reset failures. Test by reading known hardware status, exercising all queues, and validating suspend/resume on both CLDMA MD and AP instances.
