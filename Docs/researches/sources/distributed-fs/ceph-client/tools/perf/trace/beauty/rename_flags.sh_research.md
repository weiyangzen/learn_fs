# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/rename_flags.sh

Purpose: Generates `RENAME_*` flag names for `renameat2(2)`.

Important APIs/types/functions: It reads `fs.h` and emits `static const char *rename_flags[]`, indexing shift-expression values as `bit + 1`.

Control flow: Optional header directory selection is followed by a regex matching `(1 << n)` style definitions and formatting entries with `%d + 1`.

State and persistence: stdout-only generator.

Dependencies and integration points: The output is included by `renameat.c`.

Risks: Hex or decimal `RENAME_*` definitions would not match. The script assumes all relevant rename flags are one-bit shifts.

Test signals: Verify generated entries for `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`; trace `renameat2`.
