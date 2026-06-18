# sources/distributed-fs/ceph-client/tools/perf/util/bpf-filter.h

Purpose: declares BPF sample-filter expression structures and public filter lifecycle APIs.

Important APIs and types: `struct perf_bpf_filter_expr` stores list membership, optional OR-group list, operation, sample term part, term, and comparison value. `PERF_BPF_FILTER_PIN_PATH` names the bpffs pin directory. Real APIs are exposed when `HAVE_BPF_SKEL` is set: expression allocation, parse, prepare, destroy, lost-count, pin, and unpin. Stub APIs return `-EOPNOTSUPP` or zero when BPF skeleton support is absent.

Control flow: the header supports parser construction of expression lists and evsel preparation/cleanup in the implementation. Conditional compilation determines whether callers get working filtering or a clear build-time unsupported path.

State and persistence: expression nodes are in-memory list elements owned by evsels. Pinned path names persistent bpffs objects used across perf invocations.

Dependencies and integration points: includes generated sample-filter BPF definitions, debug output, Linux lists, and forward declarations for evsel/target.

Risks: stubs mean code can compile without BPF support but runtime requests fail. Expression ownership is manual; parser errors and destroy paths must free nested group entries correctly.

Test signals: build with and without BPF skeleton support, expression parse/free tests, and unsupported-mode error message tests.
