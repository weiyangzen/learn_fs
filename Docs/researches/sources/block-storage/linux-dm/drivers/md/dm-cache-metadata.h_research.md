# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.h

Declares the DM cache metadata API and feature constants. Metadata block size and maximum metadata device sectors are inherited from the metadata space map; devices larger than 16 GiB trigger a warning threshold.

The public API covers open/close, cache resize/size, discard bitset resize/load/set, mapping insert/remove/load, dirty bit import, statistics get/set, commit, free/total metadata block counts, dump, hint writing, all-clean checks, needs-check state, read-only/read-write state, and transaction abort.

Callback typedefs let callers stream discard and mapping records without exposing internal dm-array or bitset structures. `dm_cache_statistics` stores 32-bit read/write hit/miss counters persisted in the superblock.

Feature masks are ext-style compat/ro-compat/incompat placeholders and are currently all zero, so unsupported on-disk feature bits cause open failure according to the metadata implementation.
