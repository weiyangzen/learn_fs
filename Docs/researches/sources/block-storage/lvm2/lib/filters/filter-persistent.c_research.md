# File Research: sources/block-storage/lvm2/lib/filters/filter-persistent.c

This file implements a caching wrapper around another device filter. The cache maps every device alias string to either a static good marker or bad marker in a radix tree, avoiding repeated evaluation of the underlying filter chain.

`struct pfilter` stores the radix tree, wrapped real filter, and `dev_types`. `_init_hash` recreates the radix tree. `_persistent_filter_wipe` clears the entire cache when called without a device or removes all aliases for a specific device.

`_lookup_p` behavior:
- If a specific `use_filter_name` does not target this filter, or the cache tree is unavailable, it delegates directly to the wrapped filter.
- Devices with no aliases are rejected.
- Cached bad devices are rejected, cached good devices pass.
- Uncached devices are evaluated by `pf->real->passes_filter`; pass/fail is cached against every alias.
- Invalid filter return values are logged, treated as pass, and not cached.

`persistent_filter_create` initializes the wrapper named `persistent` and owns the wrapped filter; `_persistent_destroy` destroys the radix tree, destroys the wrapped filter, and frees all wrapper storage. The file explicitly notes that this cache is a workaround for repeated filter evaluation elsewhere in the scanning path.
