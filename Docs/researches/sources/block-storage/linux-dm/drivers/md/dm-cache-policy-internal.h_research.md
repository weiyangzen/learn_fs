# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-internal.h

Provides inline wrappers around the `dm_cache_policy` vtable for internal cache target use. Most wrappers directly dispatch to policy methods, while optional hooks have defaults: `lookup_with_work` falls back to `lookup`, `get_hint` returns 0, `tick` is skipped, config emission returns zero values, and setting an unsupported config returns `-EINVAL`.

Also defines bitset utility helpers used by policies: compute bitset byte size, allocate with `vzalloc`, clear with `memset`, and free with `vfree`.

The header declares policy lifecycle helpers implemented in `dm-cache-policy.c`: create by name, destroy with module reference release, and query policy name/version/hint size. It is the bridge between the public policy interface and core target internals.
