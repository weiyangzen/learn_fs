# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/parse-utils.h

Purpose: `parse-utils.h` exposes a regex-backed incremental parser helper for repeatedly extracting matches from a complete string.

Important APIs and types: `struct parser` owns a compiled `regex_t`, one `regmatch_t`, the complete string under parse, the regex text, and a temporary offset string. `parser_init`, `parser_set_string`, `parser_unset_string`, `parser_deinit`, and `parser_get_next_match` form the lifecycle.

Control flow and state: callers create a parser for a regex, set the target string, repeatedly request the next match, unset the string when done, and finally deinit. State is per-parser and not global.

Dependencies and integration: includes POSIX `<regex.h>` and uses Gluster allocation/logging in the implementation. It is useful for parsing option or command output strings without open-coding regex loops.

Risks: ownership of returned match strings is not documented in the header. Regex compilation and match offsets must handle empty matches carefully to avoid infinite loops. Parser reuse requires `parser_unset_string` discipline.

Test signals: tests should cover invalid regex, NULL/empty strings, no match, repeated matches, escaped patterns, zero-length matches, and cleanup under allocation failure.
