# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc-ops.h

## Purpose
`htc-ops.h` is the inline dispatch layer for HTC operations. It lets core/WMI code call HTC lifecycle, service connection, TX/RX buffer, activity, credit, and completion functions without knowing whether the attached HTC backend is mailbox or pipe.

## Important APIs, types, and functions
Wrappers include `ath6kl_htc_create()`, `ath6kl_htc_wait_target()`, `ath6kl_htc_start()`, `ath6kl_htc_conn_service()`, `ath6kl_htc_tx()`, `ath6kl_htc_stop()`, `ath6kl_htc_cleanup()`, `ath6kl_htc_flush_txep()`, `ath6kl_htc_flush_rx_buf()`, `ath6kl_htc_activity_changed()`, `ath6kl_htc_get_rxbuf_num()`, `ath6kl_htc_add_rxbuf_multiple()`, `ath6kl_htc_credit_setup()`, `ath6kl_htc_tx_complete()`, and `ath6kl_htc_rx_complete()`.

## Control flow and integration
Core initialization selects a backend by calling either mailbox or pipe attach, which writes `ar->htc_ops`. Later, generic code uses these wrappers to create a target, wait for firmware readiness, connect WMI/control/data services, start HTC, submit packets, add RX buffers, flush on teardown, and route bus-level pipe completions. The `target->dev->ar` path is used for most dispatches after target creation.

## State and persistence behavior
This header owns no state. It dispatches over `ar->htc_ops` and `struct htc_target` state allocated by the selected backend. Effects persist in endpoint queues, credit accounting, HIF queues, target flags, and service mappings.

## Dependencies and integration points
It includes `htc.h` and `debug.h`. It is a narrow polymorphic boundary between generic ath6kl core/WMI code and the transport implementations in `htc_mbox.c` and `htc_pipe.c`.

## Risks and test signals
The wrappers assume all ops are non-null and target backpointers are valid. Pipe-only completion wrappers call `ar->htc_ops->tx_complete/rx_complete`, which mailbox ops do not fill, so they must only be used by pipe HIF paths. Test signals include both HTC backend attach paths, service connection smoke tests, teardown flushes, and ensuring pipe completion paths are never invoked for mailbox backends.
