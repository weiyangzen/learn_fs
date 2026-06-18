# Research: sources/compression/xz/src/xz/list.h
## sources/compression/xz/src/xz/list.h

Purpose: Declares the public list-mode entry points.

Important APIs: `list_file(const char *filename)` lists one `.xz` file. `list_totals(void)` emits aggregate totals after all list-mode files have been processed.

Control flow and integration: `main.c` switches the per-file runner from `coder_run` to `list_file` when decoder support is built and `opt_mode` is `MODE_LIST`, then calls `list_totals()` after the loop.

State and persistence: State is internal to `list.c`; callers only trigger per-file and final aggregate output.

Risks: The header is only included when `HAVE_DECODERS` through `private.h`, matching the fact that list mode requires decoder support.

Test signals: Build without decoders and ensure list paths are unavailable; build with decoders and verify `main.c` dispatch.
