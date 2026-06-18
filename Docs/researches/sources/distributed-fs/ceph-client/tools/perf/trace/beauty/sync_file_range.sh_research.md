# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.sh

Purpose: Generates individual `SYNC_FILE_RANGE_*` flag names.

Important APIs/types/functions: It parses `fs.h` and emits `static const char *sync_file_range_flags[]`.

Control flow: Optional header directory selection is followed by a regex for hex/digit flag values and `ilog2(value) + 1` entry formatting.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `sync_file_range.c`, whose C logic handles the composite write-and-wait alias.

Risks: Composite or zero-valued definitions would not be handled as desired by the generated bit table.

Test signals: Regenerate and verify wait/write bit entries; compile and trace `sync_file_range`.
