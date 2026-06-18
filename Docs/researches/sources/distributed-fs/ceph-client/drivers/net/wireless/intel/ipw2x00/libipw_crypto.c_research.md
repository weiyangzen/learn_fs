# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto.c

## Purpose
Implements the shared crypto algorithm registry and per-device crypto context lifecycle for libipw. It registers a built-in `NULL` algorithm, lets WEP/TKIP/CCMP modules register `libipw_crypto_ops`, and manages delayed destruction of key contexts so RX/TX paths can finish while references are outstanding.

## Important APIs, Types, and Functions
`struct libipw_crypto_alg` links an algorithm name to a `libipw_crypto_ops`. Public functions are `libipw_crypt_info_init`, `libipw_crypt_info_free`, `libipw_crypt_delayed_deinit`, `libipw_register_crypto_ops`, `libipw_unregister_crypto_ops`, `libipw_get_crypto_ops`, `libipw_crypto_init`, and `libipw_crypto_exit`. Internal helpers are `libipw_crypt_deinit_entries`, `libipw_crypt_quiescing`, and `libipw_crypt_deinit_handler`.

## Control Flow
`libipw_crypt_info_init()` clears a per-device `libipw_crypt_info`, stores the caller's lock, initializes the delayed-deinit list, and sets up a timer. Key replacement calls `libipw_crypt_delayed_deinit()`, which unlinks the active key pointer, adds the old context to `crypt_deinit_list`, and starts a one-second timer. The timer frees entries only when their atomic refcount reaches zero, then reschedules while entries remain. Module init registers the `NULL` ops; crypto-specific modules register their own ops; lookup scans the global list under `libipw_crypto_lock`.

## State and Persistence Behavior
Global state is the `libipw_crypto_algs` list guarded by `libipw_crypto_lock`. Per-interface crypto state lives in `libipw_crypt_info`: active key pointers, default TX key index, delayed deletion list, timer, and quiesced flag. `libipw_crypt_info_free()` quiesces delayed deletion, synchronously deletes the timer, force-frees pending entries, and deinitializes all active key slots with module refcount drops.

## Dependencies and Integration Points
Depends on spinlocks, timers, atomic refcounts, module ownership, lists, and allocation. It is called by `alloc_libipw/free_libipw`, `libipw_wx.c`, and the data paths in `libipw_rx.c`/`libipw_tx.c`. Algorithm modules are `libipw_crypto_wep`, `libipw_crypto_tkip`, and `libipw_crypto_ccmp`.

## Risks
The registry lookup returns an ops pointer after dropping the global lock; module lifetime is protected only when users subsequently call `try_module_get`. Delayed deinit depends on every encrypt/decrypt path incrementing and decrementing `refcnt` correctly. If `crypt_quiesced` is set, new delayed entries are not added and the caller has already nulled the active pointer, so shutdown ordering must call force cleanup. `libipw_crypto_exit()` asserts the registry is empty after unregistering NULL, so algorithm exit ordering matters.

## Test Signals
Key replacement under traffic, module unload after active traffic, timer rescheduling with nonzero refcounts, WEP/TKIP/CCMP module load-on-demand, `free_libipw()` with pending delayed entries, duplicate/unknown algorithm lookup, and module init/exit ordering are useful validation signals.
