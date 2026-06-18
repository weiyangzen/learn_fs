# File Research: sources/block-storage/util-linux/libblkid/src/read.c

Parser for the on-disk blkid cache. It reads XML-like single-line device entries of the form `<device TAG="value"...>/dev/name</device>`, reconstructs `blkid_dev` objects in a cache, and restores direct fields such as `DEVNO`, `PRI`, and `TIME` plus generic tags like `TYPE`, `LABEL`, and `UUID`.

The parser trims whitespace, skips comments and unknown XML-ish lines, handles backslash-escaped quoted values, supports line continuations ending in backslash, and rejects malformed cache records without aborting the whole cache load. Device records without `TYPE` are discarded because the cache cannot meaningfully identify their content.

`blkid_read_cache` avoids rereading unchanged cache files by comparing `st_mtime` and the cache changed flag. It depends on cache/device/tag helpers from `blkidP.h`. Main risks are the intentionally lenient legacy cache grammar and fixed 4096-byte line buffer, though continuation support reduces ordinary truncation issues.
