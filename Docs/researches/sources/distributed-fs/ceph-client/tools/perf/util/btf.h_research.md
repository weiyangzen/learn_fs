# sources/distributed-fs/ceph-client/tools/perf/util/btf.h

## sources/distributed-fs/ceph-client/tools/perf/util/btf.h

Purpose: this header declares the BTF member lookup helper implemented in `btf.c`.

Important API: `__btf_type__find_member_by_name()` is declared with forward-declared `struct btf` and `struct btf_member`.

Control flow and state: no executable logic; it keeps users from including heavier BTF details in their headers.

Dependencies and integration: included by perf utilities that need member lookup against loaded BTF data.

Risks: the double-underscore name signals an internal helper; callers should treat returned pointers as borrowed from the BTF object lifetime.

Test signals: compile callers with only the forward declaration and run lookup tests through `btf.c`.
