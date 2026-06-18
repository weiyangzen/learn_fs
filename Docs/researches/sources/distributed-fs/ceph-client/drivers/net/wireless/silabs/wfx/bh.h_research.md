# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/bh.h

Purpose: Declares the WFx bottom-half state and request entry points.

Important APIs and types: `struct wfx_hif` stores bottom-half work, control-register readiness completion, TX sequence number, RX sequence number, atomic control register snapshot, TX buffer usage, and waitqueue for empty firmware TX buffers. Exported functions are `wfx_bh_register()`, `wfx_bh_unregister()`, `wfx_bh_request_rx()`, `wfx_bh_request_tx()`, and `wfx_bh_poll_irq()`.

Control flow and integration: Bus IRQ handlers call `wfx_bh_request_rx()`, TX producers call `wfx_bh_request_tx()`, early firmware startup may use `wfx_bh_poll_irq()`, and common probe/release bracket the lifecycle with register/unregister.

State and persistence: The header exposes the transient per-device HIF transport state embedded in `struct wfx_dev`.

Dependencies: Depends on Linux workqueue, completion, waitqueue, and atomic APIs.

Risks and test signals: Tests should verify initialization before IRQ subscription, flushing during release, waitqueue wakeups when TX credits reach zero, and sequence/credit state reset across probe failure paths.

Test signals: Source read size: 34 lines, 758 bytes.
