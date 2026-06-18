# sources/distributed-fs/ceph-client/tools/perf/util/event.c

Purpose: Implements perf event record names, event printing, machine-processing adapters, kallsyms symbol lookup helpers, stat config import, address-to-map/symbol resolution, and sample address correlation predicates.

Important APIs: `perf_event__name`, many `perf_event__fprintf_*` functions, `perf_event__fprintf`, `perf_event__process_*` adapters, `kallsyms__get_function_start`, `kallsyms__get_symbol_start`, `machine__resolve`, `thread__find_map`, `thread__find_map_fb`, `thread__find_symbol`, `thread__resolve`, `is_bts_event`, and `sample_addr_correlates_sym`.

Control flow: Processing functions mostly delegate typed records to `machine__process_*`. Printers switch on record type and format typed payloads, including mmap build IDs, namespaces, cgroups, aux flags, text poke bytes, BPF metadata, and schedstat version-specific fields. `machine__resolve` finds or creates the relevant thread, locates maps based on host/guest cpumode, applies thread/dso/symbol/parallelism filters, computes latency, and resolves symbols.

State and persistence: No persistent state is owned here. It mutates machine/thread/map state via delegated processing and fills caller-owned `addr_location` structures. Kallsyms helpers stream symbol files and return a found address.

Dependencies and integration: Bridges raw perf records to `machine`, `thread`, `map`, `dso`, `symbol`, BPF, namespace, hist, stat, and session code. Uses global symbol configuration such as host/guest filters, dso/symbol lists, lazy kernel map loading, and parallelism filters.

Risks: Record printers assume event payload layout matches header type and size. Address resolution can filter incorrectly if cpumode is missing or branch/sample address mode differs; fallback logic mitigates this. Text poke symbol lookup may load kernel maps. Schedstat printing depends on version-specific include files.

Test signals: Synthetic perf event fixtures for every printed record type, kallsyms parsing tests for function and alias symbols, host/guest cpumode resolution tests, dso/symbol filter tests, branch/page-fault address-correlation tests, and schedstat v15/v16/v17 print tests.
