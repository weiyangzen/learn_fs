# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/nocow_locking.h

## Role

`nocow_locking.h` declares no-COW bucket lock helpers and defines the hash lookup function.

## API

- `bucket_nocow_lock()`: hashes a device bucket into the fixed lock table.
- `BUCKET_NOCOW_LOCK_UPDATE`: flag selecting update lock mode.
- `bch2_bucket_nocow_is_locked()`
- `bch2_bucket_nocow_unlock()` / `__bch2_bucket_nocow_unlock()`
- `bch2_bkey_nocow_trylock()`, `bch2_bkey_nocow_lock()`, `bch2_bkey_nocow_unlock()`
- diagnostics and fs init/exit helpers

## Use

Used by write/update and data movement paths when physical buckets can be updated in place or copied.
