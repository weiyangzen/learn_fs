# File Research: sources/block-storage/stratisd/src/dbus/pool/pool_3_9/methods.rs

This file implements the new pool r9 D-Bus methods for online pool encryption lifecycle operations:
- `encrypt_pool_method`
- `reencrypt_pool_method`
- `decrypt_pool_method`

All methods follow the Stratis D-Bus return shape: operation result, `u16` return code, and return string.

`encrypt_pool_method()`:
- Parses key descriptions from D-Bus tuple-options into `Option<u32>` token slots.
- Parses Clevis JSON strings with `serde_json::from_str`.
- Builds `InputEncryptionInfo`; rejects calls with no unlock methods.
- Gets a mutable pool guard by UUID.
- Runs blocking engine operations inside `tokio::task::spawn_blocking`.
- Calls the engine/pool lifecycle:
  - `start_encrypt_pool()`
  - `do_encrypt_pool()` under downgraded read guard
  - `Engine::upgrade_pool()` back to write guard
  - `finish_encrypt_pool()`
- Emits keyring, Clevis, and encrypted-property D-Bus signals on successful creation.
- Returns identity success if the pool was already encrypted.

`reencrypt_pool_method()`:
- Gets a mutable pool guard by UUID.
- Runs `start_reencrypt_pool()`, `do_reencrypt_pool()`, and `finish_reencrypt_pool()` with the same downgrade/upgrade pattern.
- Emits `last_reencrypted_timestamp` signal when successful.

`decrypt_pool_method()`:
- Performs `decrypt_pool_idem_check()` first.
- If decryption is required, downgrades to read guard for `do_decrypt_pool()`, upgrades, then calls `finish_decrypt_pool()`.
- Emits keyring, Clevis, encrypted, and last-reencrypted signals after successful decryption.
- Returns identity success if already decrypted.

Concurrency pattern:
- Write lock is used for idempotence/setup and final state mutation.
- Long-running actual crypto/device work runs under read lock after `downgrade()`.
- `Engine::upgrade_pool()` is used to regain write access for finalization without losing the logical operation sequence.

Error handling:
- Engine and parsing errors are converted through `engine_to_dbus_err_tuple()`.
- Join errors from `spawn_blocking` are converted through `StratisError::from`.
- Missing pool is represented as `StratisError::Msg`.

Role in architecture:
- This is the D-Bus orchestration layer for r9 encryption operations. It coordinates parsing, locking, lifecycle calls, and signals but delegates actual engine semantics to the `Pool` trait.
