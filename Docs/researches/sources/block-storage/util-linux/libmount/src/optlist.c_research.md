# File Research: sources/block-storage/util-linux/libmount/src/optlist.c

This file implements `struct libmnt_optlist`, the parsed mount option container. It preserves option order while deriving cached flags and rendered option strings for specific maps and filtering modes. Options may originate from strings or bit flags, may be mapped or unknown, may be marked external-only, and may carry values, quoted values, empty `name=` separators, recursive state, and VFS/Linux-map state.

The list object tracks refcount, age, registered option maps, the built-in Linux map, per-map and all-filter caches, propagation flags, and shortcuts for remount, bind/rbind, readonly, move, silent, and recursive propagation. Allocation initializes the Linux map; map registration deduplicates maps up to `MNT_OL_MAXMAPS`.

Mutation paths are `mnt_optlist_set_optstr()`, `append_optstr()`, `prepend_optstr()`, `append_flags()`, `set_flags()`, `remove_flags()`, `insert_flags()`, `remove_opt()`, and `remove_named()`. String parsing uses `ul_optstr_next()` and `mnt_optmap_get_entry()` to attach map entries. Flag insertion walks map entries and adds only non-inverted flags that do not require mandatory values. Every mutation increments `age` and invalidates cached flag/string results.

`mnt_optlist_merge_opts()` deduplicates by walking backward and keeping the last option, removing earlier exact duplicates and opposite inverted options with the same map id. `mnt_optlist_get_flags()` computes map ids after applying inversion semantics and respects filters: default, all, unknown, helpers, or mtab. `mnt_optlist_strdup_optstr()` renders options back to a comma-separated string, places `rw`/`ro` first for generic Linux-facing strings, filters by target audience, and preserves empty values and quoting.

When `USE_LIBMOUNT_MOUNTFD_SUPPORT` is enabled, `mnt_optlist_get_attrs()` converts selected classic `MS_*` flags to `MOUNT_ATTR_*` set/clear masks for `mount_setattr()`. It handles remount reset semantics, recursive vs nonrecursive options, atime mutual exclusion, and `ro=fs` versus VFS-only readonly handling.

Accessor helpers expose option names, values, maps, map entries, external state, `sepnodata`, and substring matching within comma-separated option values. The test program exercises string/flag insertion, setting, rendering, splitting, flag extraction, and value containment.
