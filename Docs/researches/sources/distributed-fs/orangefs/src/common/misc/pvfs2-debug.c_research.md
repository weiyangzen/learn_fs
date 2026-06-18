# sources/distributed-fs/orangefs/src/common/misc/pvfs2-debug.c

Purpose: Converts human-readable debug keyword strings into gossip debug masks and exposes keyword iteration for tools and configuration parsing.

Important APIs and functions: `PVFS_debug_eventlog_to_mask` maps general debug keywords through `s_keyword_mask_map`; `PVFS_kmod_eventlog_to_mask` maps kernel-module keywords through `s_kmod_keyword_mask_map`; `PVFS_debug_get_next_debug_keyword` returns the keyword at a numeric position or `NULL` when exhausted. Local `debug_to_mask` implements token parsing and ordered mask mutation.

Control flow: `debug_to_mask` duplicates the input string, tokenizes on comma and space, treats a leading `-` as a mask-clear operation, searches the selected keyword table, and applies each recognized token in order. Unknown tokens are ignored. A `NULL` input returns zero.

State and persistence: Stateless apart from heap allocation of the temporary token buffer. It reads static keyword tables provided by `pvfs2-debug.h`; no persistent configuration is written.

Dependencies and integration points: Used by OrangeFS command-line tools, system initialization, and logging setup paths that accept event-log strings. Depends on `pvfs2-debug.h` for generated/static maps and on standard C allocation/string routines.

Risks: `strdup` failure is not checked before `strtok`, which can crash on allocation failure. The `negate` flag is not reset per token, so once a `-keyword` is seen, later tokens in the same string are also treated as negated. Unknown keywords silently do nothing, making typo detection difficult.

Test signals: Parse empty, `NULL`, single, multiple comma/space-separated, unknown, and ordered positive/negative keyword strings. Include a regression test showing whether negation should apply only to one token. Iterate `PVFS_debug_get_next_debug_keyword` from `-1`, valid positions, and one past the end.
