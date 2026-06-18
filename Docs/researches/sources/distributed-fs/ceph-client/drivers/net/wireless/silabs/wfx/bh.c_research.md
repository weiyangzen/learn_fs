# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.c

Purpose: Implements the WFx interrupt bottom half, serializing host-to-chip command/data transmission and chip-to-host message reception on a high-priority workqueue.

Important APIs and functions: `wfx_bh_register()` initializes work/completions/waitqueue; `wfx_bh_unregister()` flushes work. `wfx_bh_request_rx()` reads the control register on IRQ, saves `hif.ctrl_reg`, completes `ctrl_ready`, and queues work. `wfx_bh_request_tx()` queues work for pending commands or data. `wfx_bh_poll_irq()` polls control state during early boot. Internals include `device_wakeup()`, `device_release()`, `rx_helper()`, `bh_work_rx()`, `tx_helper()`, `bh_work_tx()`, `ack_sdio_data()`, and `bh_work()`.

Control flow and integration: The worker wakes the chip via optional GPIO, loops through up to 32 TX messages and 32 RX messages until both drain, acknowledges SDIO data after RX, and releases the chip when no TX buffers are in use. TX prioritizes synchronous `hif_cmd` requests over queued data frames, tracks firmware input-buffer credits in `hif.tx_buffers_used`, and assigns HIF sequence numbers. RX sizes come from `CTRL_NEXT_LEN_MASK` in the control register or piggyback trailer; messages are validated, confirmations decrement TX credits, sequence numbers are checked, and SKBs are handed to `wfx_handle_rx()`.

State and persistence: Uses `wdev->hif.ctrl_ready`, atomic `ctrl_reg`, TX/RX sequence counters, `tx_buffers_used`, `tx_buffers_empty`, workqueue state, optional wakeup GPIO, and firmware-advertised input-buffer count/size. This state is transient but data-path critical.

Dependencies: Depends on HWIO register access, bus `align_size()`, mac80211 SKBs, HIF command IDs, `wfx_tx_queues_get()`, and `wfx_handle_rx()`.

Risks and test signals: Risks include lost IRQ/control-register races, piggyback length mismatch, TX credit underflow, wakeup GPIO timeout, command/data starvation, and SDIO error bits left uncleared. Test IRQ RX, polled startup RX, command confirm, multi-TX confirm credit release, queued data TX, firmware sleep/wake races, malformed length handling, and flush/unregister while work is pending.

Test signals: Source read size: 324 lines, 8840 bytes.
