# File Research: sources/block-storage/util-linux/libblkid/src/resolve.c

Small cache lookup API for resolving device names and tag values. `blkid_get_tag_value` finds a tag such as `LABEL` or `UUID` on a named device and returns a duplicated string. `blkid_get_devname` accepts either `NAME=value`, a `(name,value)` pair, or a raw device name; tag inputs are resolved through the blkid cache and raw device names are copied through unchanged.

If no cache is supplied, both functions create and release a default cache internally. The code relies on `blkid_get_cache`, `blkid_get_dev`, `blkid_find_tag_dev`, `blkid_parse_tag_string`, and `blkid_find_dev_with_tag`. Behavior is intentionally simple: no probing is done here directly beyond whatever cache acquisition does, and all returned strings are caller-owned.
