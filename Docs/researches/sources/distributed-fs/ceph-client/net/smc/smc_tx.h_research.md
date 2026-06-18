# sources/distributed-fs/ceph-client/net/smc/smc_tx.h

Purpose: Declares SMC transmit entry points and exposes the prepared-send cursor helper used to decide whether data is waiting for transfer.

Important APIs/types/functions: `smc_tx_prepared_sends()` computes the difference between `tx_curs_sent` and `tx_curs_prep` in the send buffer ring. Public functions initialize TX callbacks, send user messages, push nonempty send buffers, wake producers when space returns, send consumer updates, run deferred TX work, and perform SMC-D ISM writes.

Control flow: Send paths call `smc_tx_sendmsg()` to stage bytes, then `smc_tx_sndbuf_nonempty()`/`smc_tx_pending()` to transmit staged bytes. Receive paths call `smc_tx_consumer_update()` after consuming RMB data. Workqueue code invokes `smc_tx_work()` when a send could not complete immediately.

State and persistence behavior: The header does not own state; it operates on `struct smc_connection` cursors, buffer descriptors, link-group transport type, and socket callbacks.

Dependencies and integration points: Depends on socket types, SMC core definitions, and CDC cursor/control structures. It bridges AF_SMC socket code, RX consumer updates, CDC, SMC-D, and SMC-R WR code.

Risks and test signals: Risks are stale cursor differences or callers invoking APIs without required socket/send locking. Test compile users, prepared-send detection across wrap, RX-triggered consumer updates, SMC-D write callers, and deferred TX work after WR slot pressure.
