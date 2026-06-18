# File Research: sources/block-storage/util-linux/libblkid/src/verify.c

## Scope

Implements cache entry verification against current block-device state.

## Behavior

- `blkid_verify()` checks stat timestamps and a minimum re-probe interval to avoid unnecessary probing.
- Returns unverified cached data on permission/not-found access failures, but removes entries on other stat/open failures.
- Skips private device-mapper nodes.
- Reuses a cache-level probe to run safe superblock and partition probing, clears old tags, then repopulates current tags.
- Converts `PART_ENTRY_UUID`/`PART_ENTRY_NAME` into `PARTUUID`/`PARTLABEL` and suppresses auxiliary `_ID` tags from cache tags.

## Dependencies And Risks

- Mutates cache and device tag state during verification.
- Requires careful fd reset and filter reset after probing.
- Timestamp logic differs depending on nanosecond stat support.
