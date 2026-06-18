# File Research: sources/block-storage/util-linux/libmount/src/optstr.c

This file implements the low-level mutable string API for comma-separated mount option strings. It predates and complements `optlist.c`; callers can append, prepend, locate, set, remove, deduplicate, split, map to flags, apply flags, and match option patterns without building a `libmnt_optlist`.

The internal `libmnt_optloc` records the beginning, end, value pointer/length, and name length of a located option. `mnt_optstr_locate_option()` iterates with `ul_optstr_next()` and matches exact parsed names. `mnt_buffer_append_option()` is the central renderer: it inserts commas as needed, writes `name`, optionally writes `=`, preserves empty value syntax (`name=`), and optionally quotes values.

Mutation helpers include `mnt_optstr_append_option()`, `mnt_optstr_prepend_option()`, `mnt_optstr_set_option()`, `mnt_optstr_remove_option()`, `mnt_optstr_remove_option_at()`, and `mnt_optstr_deduplicate_option()`. `insert_value()` handles in-place reallocation and insertion of `=value` at a recorded offset. Removal ensures results do not start/end with commas or contain doubled commas.

Classification helpers include `mnt_split_optstr()` and `mnt_optstr_get_options()`. They parse each option, look it up in the built-in Linux and userspace maps or a supplied map, ignore map entries with no id, ignore value-bearing instances for no-value map entries, and append selected options into newly allocated user/VFS/FS/subset strings while respecting ignore masks.

`mnt_optstr_get_missing()` compares a wanted option string against an existing string and optionally returns a newly allocated list of missing options. `mnt_optstr_get_flags()` sets and clears bits in a caller-supplied flag word according to a map, with special translation of userspace `user`/`users`/`owner`/`group` into secure kernel flags when extracting Linux flags.

`mnt_optstr_apply_flags()` is deprecated but still implements string rewriting from a flag mask. It normalizes leading `ro`/`rw`, removes mapped options not present in the mask, preserves multi-use prefix options, and appends missing non-inverted no-value map entries. `mnt_match_options()` implements mount-style pattern matching, including `no` negation and `+` literal-prefix handling.
