# Research: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/topdown.h

Purpose: provides the x86 topdown helper prototype needed by generic perf topdown/stat code.

Important APIs/types/functions: declares `topdown_sys_has_perf_metrics()`.

Control flow: no runtime control flow; guarded by `_X86_TOPDOWN_H`.

State and persistence: no state.

Dependencies and integration: paired with `topdown.c` and generic `util/topdown.h` consumers.

Risks: minimal; declaration must match implementation signature.

Test signals: x86 perf build and link of topdown code.
