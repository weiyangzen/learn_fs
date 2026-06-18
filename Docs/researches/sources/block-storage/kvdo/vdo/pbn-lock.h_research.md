# File Research: sources/block-storage/kvdo/vdo/pbn-lock.h

## Purpose
Defines PBN lock types, lock state, and lock operations.

## Key Definitions
- `enum pbn_lock_type`: read, data write, block-map write.
- `struct pbn_lock`: implementation pointer, holder count, compressed fragment lock count, provisional-reference flag, read-lock increment limit, and atomic claimed-increment count.

## API Surface
Initialization, read-lock check, write-to-read downgrade, increment claim, provisional-reference assign/unassign/release.

## Integration Notes
PBN locks are used by physical zones, dedupe, compressed writes, and block reference accounting. The inline `vdo_pbn_lock_has_provisional_reference` safely handles NULL locks.
