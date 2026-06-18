# File Research: sources/cow-pools/bcachefs-tools/fs/data/nocow_locking.h

## Purpose
Public API and hashing helper for no-COW bucket locking.

## Main Interfaces
- `bucket_nocow_lock()` hashes a packed bucket id with `hash_64()` into `BUCKET_NOCOW_LOCKS` buckets.
- `BUCKET_NOCOW_LOCK_UPDATE` selects update-lock sign; absence is copy-lock sign.
- Declares bucket lock query/unlock, bkey pointer lock/unlock/trylock, text rendering, and filesystem init/exit.

## Dependencies
Includes bcachefs core, allocation background helpers, lock types, and Linux hash helpers.
