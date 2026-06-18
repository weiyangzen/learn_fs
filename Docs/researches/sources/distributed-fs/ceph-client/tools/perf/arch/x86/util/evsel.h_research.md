# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.h

Purpose: This local x86 perf utility header exposes the topdown capability predicate implemented in `evsel.c` to neighboring x86 util files.

Important APIs, types, and functions: The only declaration is `bool evsel__sys_has_perf_metrics(const struct evsel *evsel);`. The header relies on including code to have a visible declaration of `struct evsel` and `bool` from other headers.

Control flow: There is no runtime control flow in this header. It provides an include guard `_EVSEL_H` and a function prototype.

State and persistence: No state is stored or persisted.

Dependencies and integration points: `arch/x86/util/evlist.c` includes this header to call the predicate while sorting and inserting topdown events. The implementation lives in `arch/x86/util/evsel.c`.

Risks: The generic name `_EVSEL_H` is broad and could collide if include ordering changes, although it is local to the x86 util directory. Any signature change must be synchronized with the implementation and callers.

Test signals: Build success is the main signal. Topdown parse and grouping tests exercise the caller side of this declaration.
