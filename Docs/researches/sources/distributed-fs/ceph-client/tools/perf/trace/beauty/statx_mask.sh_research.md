# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx_mask.sh

Purpose: Generates the `STATX_*` mask bit table.

Important APIs/types/functions: It reads the beauty copy of `uapi/linux/stat.h` and emits `static const char *statx_mask[]`.

Control flow: The script matches hex `STATX_*` definitions, filters `STATX_ALL`, `STATX_BASIC_STATS`, and `STATX_ATTR_*`, and indexes each remaining bit as `ilog2(value) + 1`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `statx.c`.

Risks: Composite masks and attribute masks are deliberately excluded. Decimal or expression-valued definitions are ignored.

Test signals: Regenerate and confirm entries for core statx request bits; compile and trace statx.
