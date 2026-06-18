## sources/distributed-fs/ceph-client/tools/lib/cmdline.c

Purpose: Provides `memparse()`, a kernel-style parser for numeric memory-size strings with binary suffixes.

Important APIs/functions: `memparse(const char *ptr, char **retptr)` parses a base-0 integer using `strtoll`, then applies cascading left shifts for suffixes `K`, `M`, `G`, `T`, `P`, and `E` in either case.

Control flow: After parsing the numeric prefix, a switch deliberately falls through from larger suffixes to smaller suffixes, shifting by 10 each step. It advances `endptr` only when a recognized suffix is consumed, then optionally returns the final parse position.

State/persistence: Stateless.

Dependencies/integration: Uses libc `strtoll` and local `fallthrough` annotation. Tools can use it to parse kernel-like size options.

Risks: Overflow is unchecked during shifts. Negative text can pass through `strtoll` and then convert to unsigned result. Suffixes are binary powers, not decimal SI.

Test signals: Cover bare values, hex/octal prefixes, each suffix and case, trailing garbage and `retptr`, overflow/negative inputs, and empty strings.
