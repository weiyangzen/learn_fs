# File Research: sources/block-storage/lvm2/lib/filters/filter-regex.c

This file implements the user-configured regex device filter. Patterns are config strings beginning with `a` or `r`, followed by a delimiter and a regex, for example accept or reject rules. `_extract_pattern` parses the action, recognizes paired delimiters such as parentheses/brackets/braces, strips the trailing separator, and records whether the indexed pattern accepts.

`_build_matcher` validates the config list, allocates a scratch pool, reverses the configured order when building the matcher to get the desired first-match precedence, creates a bitset of accepting patterns, and builds a `dm_regex` engine in the filter memory pool.

`_accept_p` clears `DEV_FILTERED_REGEX` and may bypass regex filtering when a devices list is active, when `filter_regex_skip` is set, or when the devices file is enabled without `filter_regex_with_devices_file`. In the devices-file bypass case it emits one-time warnings that `filter` or `global_filter` is ignored.

When active, it tests all aliases. The first matching accept passes the device and may set the preferred name if a non-first alias matched. Matching rejects mark the device rejected; aliases that match nothing pass by default unless a reject was seen. `regex_filter_create` owns all memory through a dm pool and names the filter `regex`.
