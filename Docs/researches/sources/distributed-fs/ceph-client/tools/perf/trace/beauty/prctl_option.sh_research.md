# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/prctl_option.sh

Purpose: Generates string arrays for `prctl(2)` option names and `PR_SET_MM_*` suboptions.

Important APIs/types/functions: It emits `static const char *prctl_options[]` and `static const char *prctl_set_mm_options[]` from the beauty copy of `uapi/linux/prctl.h`.

Control flow: The first pass matches `PR_*` definitions, excludes `PR_SET_PTRACER`, sorts numerically, and prints entries. The second pass matches `PR_SET_MM_*` definitions and emits a separate suboption table.

State and persistence: Stateless stdout generation.

Dependencies and integration points: Output is included by `prctl.c`.

Risks: The option regex expects a specific one-space `#define` style and mostly numeric values; formatting changes can omit options. Excluding `PR_SET_PTRACER` is intentional but should be reviewed if perf wants it displayed.

Test signals: Regenerate and compile; confirm names for common `PR_*` and `PR_SET_MM_*` values are present.
