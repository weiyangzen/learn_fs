# sources/compression/xz/src/xz/util.c

Purpose: provides utility routines for the full `xz` command: fatal allocation wrappers, numeric option parsing, human-readable formatting, bounded string construction, and terminal detection.

Important APIs: implements `xrealloc()`, `xstrdup()`, `str_to_uint64()`, `round_up_to_mib()`, `uint64_to_str()`, `uint64_to_nicestr()`, `my_snprintf()`, `is_tty()`, `is_tty_stdin()`, and `is_tty_stdout()`. The formatting functions share four static 128-byte buffers indexed by caller-supplied slot.

Control flow: allocation failures free the old pointer before `message_fatal()` to increase the chance that diagnostics can allocate memory. `str_to_uint64()` manually parses non-negative decimal text, accepts `"max"`, supports binary `K/M/G` suffix variants, checks overflow before each multiply/add, and enforces `[min, max]`. Formatting probes thousands-separator support at runtime except on known-broken platforms. TTY wrappers report user-facing errors for terminal stdin/stdout.

State and persistence: state is process-local: `bufs[4][128]` and a cached thousand-separator status. No persistent files are affected.

Dependencies and integration: depends on `private.h`, gettext/message helpers, `tuklib_mask_nonprint()`, libc allocation and formatting, POSIX `isatty()`, and Windows console APIs. It is used throughout option parsing, progress/status output, and safety checks that prevent binary data from being read from or written to terminals.

Risks: static buffers are not thread-safe and are overwritten by subsequent calls using the same slot. `xmalloc`/`xrealloc` must not be used while incomplete output needs cleanup, as documented in `util.h`. Locale-dependent thousands formatting is probed defensively but still depends on `snprintf()` behavior.

Test signals: no direct unit test in this subset. Indirect coverage comes through command option parsing, memlimit strings, messages, and shell tests. High-value tests would include overflow suffix parsing, malformed suffix diagnostics, Windows TTY handling, and buffer truncation behavior in `my_snprintf()`.
