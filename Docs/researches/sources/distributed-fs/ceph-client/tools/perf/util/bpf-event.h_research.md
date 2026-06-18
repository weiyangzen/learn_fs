# sources/distributed-fs/ceph-client/tools/perf/util/bpf-event.h

Purpose: declares BPF event processing and BPF program metadata structures for perf.

Important APIs and types: `struct bpf_metadata` owns a metadata perf event plus synthesized program names. `struct bpf_prog_info_node` stores a linearized `bpf_prog_info`, optional metadata, and an rbtree node for `perf_env`. `struct btf_node` stores raw BTF by id. Public APIs under libbpf support include `machine__process_bpf()`, `evlist__add_bpf_sb_event()`, `__bpf_event__print_bpf_prog_info()`, and `bpf_metadata_free()`. Stub implementations no-op when libbpf support is absent.

Control flow: no implementation flow in the header; conditional compilation selects real APIs or no-op stubs based on `HAVE_LIBBPF_SUPPORT`.

State and persistence: structures are stored in perf environment rbtrees and persist for the session lifetime.

Dependencies and integration points: includes rbtree, fd array API, and forward declares perf session/machine/sample/env types. It bridges BPF event synthesis, sideband event collection, and report-time symbolization.

Risks: users built without libbpf support get silent no-op BPF processing, so feature availability must be surfaced elsewhere. Ownership of `perf_bpil` and metadata is explicit but easy to leak if insertion into env fails.

Test signals: build with and without libbpf, env insertion/free tests, and BPF annotation tests that retrieve `bpf_prog_info_node` and `btf_node` from the environment.
