# File Research: sources/block-storage/util-linux/libblkid/src/save.c

Writer for the blkid cache file. It serializes non-removable cache devices with known types into `<device ...>path</device>` records, quoting tag values and escaping only `"` and `\`. Device metadata includes `DEVNO`, `TIME`, optional `PRI`, and all tags attached to the device.

`blkid_flush_cache` skips unchanged or empty caches, creates the default runtime directory when needed, checks write access, and prefers a temporary file in the same directory for regular cache files. On successful temp-file writes it creates a `.old` hard-link backup when possible and renames the temp file into place.

The file depends on `mkstemp_cloexec`, `close_stream`, and blkid cache/list structures. Error handling is conservative: inability to write the cache often returns success-like no-op behavior so probing tools are not failed just because persistence is unavailable.
