# sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v0.c

### Purpose
This test dlfilter validates backward compatibility with the original v0 perf dlfilter C API. It intentionally copies the old struct and function table definitions instead of including the current header.

### Important APIs, Types, And Functions
The local v0 `struct perf_dlfilter_sample`, `struct perf_dlfilter_al`, and `struct perf_dlfilter_fns` define the ABI being tested. `start()` validates `--dlarg` argument delivery and allocates `filter_data`. `filter_event_early()` and `filter_event()` call `do_checks()` to validate sample fields, address resolution, event attributes, and object-code reads. `stop()` checks lifecycle ordering and frees state.

### Control Flow
The test expects exactly one early callback and one normal callback unless early filtering is configured to suppress the normal event. It compares sample fields against fixed test values, checks symbol resolution for `foo` and `bar`, verifies `resolve_address()` matches `resolve_ip()`, and returns either keep/filter results according to `do_early`.

### State And Persistence
State is one heap-allocated `filter_data` pointer plus counters proving callback ordering. It is released in `stop()`.

### Dependencies And Integration Points
It is used by perf's dlfilter API test harness, which must synthesize expected sample values, dlargs, symbols, attr data, and object code.

### Risks
The test is deliberately strict; changes in fixture values or event naming require coordinated updates. Because it embeds the old ABI, it must not be mechanically changed to match the current header.

### Test Signals
The `dlfilter C API` perf test should load this shared object and pass under both keep and early-filter modes, proving v0 layout and function slots still work.
