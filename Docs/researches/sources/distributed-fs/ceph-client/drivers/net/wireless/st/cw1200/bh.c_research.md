# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.c

Purpose: Implements the CW1200 bottom-half service loop that connects device interrupts, WSM RX/TX processing, firmware queue buffers, and chip sleep/wake management.

Important APIs and functions: Public entry points are `cw1200_register_bh`, `cw1200_unregister_bh`, `cw1200_irq_handler`, `cw1200_bh_wakeup`, `cw1200_bh_suspend`, `cw1200_bh_resume`, `cw1200_enable_powersave`, and `wsm_release_tx_buffer`. Internal helpers include `cw1200_bh_read_ctrl_reg`, `cw1200_device_wakeup`, `cw1200_bh_rx_helper`, `cw1200_bh_tx_helper`, and the main `cw1200_bh` worker.

Control flow: Registration creates a high-priority workqueue and queues the BH worker. IRQ handlers disable device interrupts under bus lock and increment `bh_rx`. TX producers increment `bh_tx`. The loop sleeps on `bh_wq`, periodically wakes for interrupt-loss detection or power-down, reads the control register, drains one or two RX frames based on `NEXT_LEN`, feeds TX if firmware input buffers are available, then re-enables interrupts. Suspend requests transition through `CW1200_BH_SUSPEND`, `CW1200_BH_SUSPENDED`, `CW1200_BH_RESUME`, and `CW1200_BH_RESUMED`.

State and persistence: State lives in `cw1200_common`: atomics for RX/TX/term/suspend, WSM sequence numbers, hardware buffer counts, sleep flags, and wait queues. It is reset on BH registration and destroyed on unregister. Fatal errors set `bh_error`.

Dependencies and integration: Depends on `hwio` for register/data I/O, `hwbus_ops` locking and IRQ enable, WSM handlers for RX/TX command framing, queue timestamp checks, firmware DPLL setup, and debug counters.

Risks: This file is concurrency-critical. Lost interrupts, stale `hw_bufs_used`, bad control lengths, or missed TX confirmations can terminate the BH and set a fatal error. RX length validation relies on firmware control fields and aligned bus reads. Power-save writes to the control register must not race active transfers.

Test signals: Exercise interrupt-driven RX/TX, TX bursts up to `wsm_caps.input_buffers`, scan wake holdoff, suspend/resume, missed-interrupt recovery, firmware exception handling, and timeout paths that warn about stuck TX confirms.
