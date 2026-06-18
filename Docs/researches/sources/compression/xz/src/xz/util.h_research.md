# sources/compression/xz/src/xz/util.h

Purpose: declares miscellaneous utility functions and formatting enums for the full `xz` command.

Important APIs and types: defines `xmalloc(size)` as `xrealloc(NULL, size)`, declares `xrealloc()`, `xstrdup()`, `str_to_uint64()`, `round_up_to_mib()`, `uint64_to_str()`, `uint64_to_nicestr()`, `my_snprintf()`, `is_tty()`, `is_tty_stdin()`, and `is_tty_stdout()`. `enum nicestr_unit` controls minimum and maximum display units from bytes through TiB.

Control flow and integration: the header documents fatal behavior for allocation and numeric parsing helpers. Formatting APIs return pointers to shared internal buffers selected by a slot. Terminal helpers centralize CLI safety policy for stdin/stdout.

State and persistence: no state is defined here, but the comments document hidden static buffers in `util.c` and the cleanup hazard of fatal allocation wrappers.

Dependencies: uses liblzma attributes such as `lzma_attr_alloc_size` and printf-format annotations. Consumers must include the command's common type setup first.

Risks: misuse of `xmalloc()` while output cleanup is required can bypass cleanup because failures are fatal. Reusing formatting slots can overwrite strings before they are printed. `my_snprintf()` silently stops appending after truncation or formatting error by setting `left` to zero.

Test signals: compile coverage plus integration tests for option parsing and terminal checks. Focused tests should validate the documented allocation and static-buffer contracts.
