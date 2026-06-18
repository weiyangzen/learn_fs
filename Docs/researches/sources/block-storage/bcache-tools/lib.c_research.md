# File Research: sources/block-storage/bcache-tools/lib.c

`lib.c` is the main shared implementation for discovery, sysfs control, and superblock conversion. It scans `/sys/block`, reads candidate devices from `/dev`, validates bcache magic/checksum/features, builds `struct dev` entries, resolves backing-device sysfs locations, maps bcache device names and attach UUIDs, and implements sysfs writes for register, unregister, stop, attach, detach, cache mode, and label.

It also converts between `cache_sb_disk` and `cache_sb`, including little-endian conversion, feature fields, large-bucket decoding, and large-bucket encoding. `set_bucket_size` upgrades cache devices to feature-aware version when bucket size exceeds `USHRT_MAX`.

Notable risks: many path buffers are fixed-size and filled with `sprintf`; `get_cachedev_state` calls `closedir(dir)` even when `opendir` failed; several helper buffers assume `/dev/` plus short kernel block names.
