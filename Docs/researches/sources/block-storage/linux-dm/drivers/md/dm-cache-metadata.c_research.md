# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.c

Implements persistent metadata for the DM cache target. The on-disk superblock stores checksum, flags, version, policy name/version/hint size, roots for mapping/hint/discard/dirty structures, cache geometry, feature flags, and statistics. Supported metadata versions are 1 and 2; v2 stores dirty bits in a separate disk bitset instead of in mapping flags.

The metadata object owns a block manager, transaction manager, metadata space map, dm-array mapping/hint metadata, discard and dirty bitsets, superblock-derived roots, rwsem locking, reference counting, and fail/read-only state. A global table keyed by block device prevents multiple active metadata instances for the same metadata device during table reloads.

Open/format flow checks whether the superblock is all zeroes, formats if permitted, validates checksum/magic/version/features, opens transaction manager and space map roots, then clears the clean-shutdown flag at transaction start. Commits flush dirty/discard bitsets, pre-commit the transaction manager, save the space-map root, update all superblock fields, set or clear clean shutdown, commit, and begin a new transaction.

Mappings are stored in a dm-array indexed by cache block. Each 64-bit value packs origin block in the high 48 bits and flags in the low 16 bits. Public operations resize the cache only if truncated blocks are unmapped or clean, insert/remove mappings, load mappings into a policy, set dirty bits, load discards, update stats, write policy hints, and test whether all cache blocks are clean.

Crash semantics are conservative: if metadata was not cleanly shut down, loaded mappings and discards are treated as dirty/not discarded as appropriate. `NEEDS_CHECK` can be set in the superblock, read-only mode delegates to the block manager, and abort destroys/reopens persistent objects; if rollback fails, `fail_io` blocks all further operations except close.
