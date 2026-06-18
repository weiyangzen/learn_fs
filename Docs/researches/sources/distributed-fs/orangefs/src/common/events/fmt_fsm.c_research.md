# sources/distributed-fs/orangefs/src/common/events/fmt_fsm.c

Purpose: Implements a small C++ format-string finite-state parser and serializer for TAU trace event varargs.

Important APIs/functions: `ff_format::parse()` scans `v_fmt` and fills up to 16 `ff_pattern` entries. `ff_pattern::parse()` recognizes `%u`, `%d`, `%f`, `%c`, and up to two `l` length modifiers. `ff_format::suck()` and `ff_pattern::suck()` pull typed values from a `va_list` into a byte buffer. `bfprint()` variants print values back from a byte buffer.

Control flow: The parser walks the format string looking for `%`, transitions through pattern/length/type states, records type size, and returns the number of characters consumed. Higher-level `ff_format::parse()` keeps advancing even on bad patterns, accumulating valid ones. Serialization iterates parsed patterns and advances a byte offset by each pattern size.

State/persistence: Parsed state is stored in `ff_format` fields: raw format, parsed format, pattern array, count, total byte size, and initialized flag. No disk persistence.

Dependencies/integration: Built as C++ via module flags. Used by `pvfs_tau_api.c` to encode start/stop event payloads into TAU user events.

Risks: No guard against more than 16 patterns, so long formats can overflow `patns`. `strncat(v_parsed_fmt, ..., 255)` ignores remaining capacity. Byte-buffer casts can violate alignment on strict platforms. `bfprint()` loop permits `totwrote <= src_sz`, which can enter with no remaining bytes.

Test signals: Unit-test supported formats, invalid formats, many-pattern overflow boundaries, vararg promotion for `float` and `char`, and round-trip encode/print across 32/64-bit builds.
