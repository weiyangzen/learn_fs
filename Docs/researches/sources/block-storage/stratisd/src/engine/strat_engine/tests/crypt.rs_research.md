# File Research: sources/block-storage/stratisd/src/engine/strat_engine/tests/crypt.rs

## Purpose
Provides encryption-test helpers for creating, installing, changing, and cleaning up random keys in the kernel keyring.

## Main Components
- `generate_random_key()` fills secure memory from `/dev/urandom` and stores it through `StratKeyActions::set_no_fd()`.
- `set_up_key()` creates a `KeyDescription` and generates associated random key data.
- `insert_and_cleanup_key()` runs a test with one installed key description and always unsets it afterward, preserving panic behavior.
- `insert_and_remove_key()` runs a pre-test with the key installed, then removes the key and runs a post-test with the raw key memory.
- `insert_and_cleanup_two_keys()` installs two key descriptions for tests needing key rotation or multiple-key scenarios.
- `change_key()` regenerates key material for an existing key description.

## Behavior
Cleanup is protected with `catch_unwind()`/`resume_unwind()` so test panics do not skip key removal. Key unsetting uses a fresh `StratKeyActions` instance backed by an unbounded Tokio channel.

## Research Notes
These helpers isolate kernel-keyring setup from pool encryption tests. They are used by Clevis/keyring and online encryption/reencryption/decryption tests in `pool/v2.rs` and elsewhere.
