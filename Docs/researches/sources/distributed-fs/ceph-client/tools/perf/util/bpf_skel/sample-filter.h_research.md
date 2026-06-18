# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample-filter.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/sample-filter.h

Purpose: this shared header defines the BPF sample-filter bytecode-like ABI used to filter perf samples in kernel context.

Important types and constants: `MAX_FILTERS`, `MAX_IDX_HASH`, and `MAX_EVT_HASH` size filter machinery. `enum perf_bpf_filter_op` defines comparison, bitwise-and, grouping, and done operations. `enum perf_bpf_filter_term` maps supported sample fields and helper-derived UID/GID terms. `struct perf_bpf_filter_entry` holds one operation term/value. `struct idx_hash_key` keys per-event/per-tgid filter selection.

Control flow and state: there is no executable logic; user space fills arrays of entries, and `sample_filter.bpf.c` interprets them sequentially.

Dependencies and integration: included by BPF and user-space code that compile/load sample filters. Term numbering intentionally corresponds to `PERF_SAMPLE_*` bit positions for many sample fields.

Risks: enum value changes break filter interpretation and static assertions in the BPF program. `MAX_FILTERS` bounds expression complexity; unsupported sample terms return zero in the BPF interpreter.

Test signals: compile-time sample-bit assertions, filters using every supported operation/term, grouped OR-like expressions, and event/tgid indexed filters.
