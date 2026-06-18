# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/madvise_behavior.sh

Purpose: Generates symbolic names for `madvise(2)` behavior values.

Important APIs/types/functions: It emits `static const char *madvise_advices[]` by parsing `MADV_*` decimal definitions from `mman-common.h`.

Control flow: Optional header directory selection is followed by a grep/sed/sort pipeline and `xargs printf` entry generation.

State and persistence: The script is stateless and writes generated C to stdout.

Dependencies and integration points: `mmap.c` includes the generated `madvise_behavior_array.c` and calls it from `syscall_arg__scnprintf_madvise_behavior`.

Risks: It only recognizes decimal values, so hex or expression-valued `MADV_*` definitions would be ignored. Duplicate or alias definitions may overwrite array slots depending on output order.

Test signals: Generate against current headers and trace `madvise` with common values such as `MADV_DONTNEED`; unknown values should print numerically.
