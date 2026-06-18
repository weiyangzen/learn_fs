# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp_type.sh

Purpose: Generates a C string array for `KCMP_*` comparison types.

Important APIs/types/functions: The script accepts an optional header directory, defaults to `tools/include/uapi/linux/`, greps `kcmp.h`, excludes `KCMP_TYPES`, and emits `static const char *kcmp_types[]`.

Control flow: It prints the array prologue, extracts enum assignments matching `KCMP_(\w+)`, transforms full names into index/name pairs with `sed`, formats entries with `xargs printf`, and prints the epilogue.

State and persistence: It writes generated C to stdout only; persistence is handled by the build rule redirecting output.

Dependencies and integration points: The output is included by `kcmp.c`. It depends on POSIX shell, `grep`, `sed -r`, and `xargs`.

Risks: The regex assumes enum entries have leading whitespace and a comma. If the header changes to macro definitions or initializer expressions, values may be dropped.

Test signals: Run the generator against the target UAPI header and compile `kcmp.c`; confirm every public `KCMP_*` except sentinel values appears in the array.
