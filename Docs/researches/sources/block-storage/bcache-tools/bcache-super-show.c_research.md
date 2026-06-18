# File Research: sources/block-storage/bcache-tools/bcache-super-show.c

`bcache-super-show` opens one device, reads a `cache_sb_disk` from `SB_START`, converts it with `to_cache_sb`, validates magic, expected sector, and CRC64 checksum, then prints decoded bcache superblock fields. `-f` allows display to continue after checksum mismatch.

It distinguishes cache-device versions `0`, `3`, `5` from backing-device versions `1`, `4`, `6`. Cache devices print cache layout, discard/order flags, device position, and replacement policy. Backing devices print data offset, cache mode, and cache state. It also rejects a possible experimental backing format when version supports offset but unexpected key data is present.
