# sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-test-api-v2.c

### Purpose
This test dlfilter validates the v2 perf dlfilter API, including the `machine_pid`/`vcpu` sample extension marker and `al_cleanup()` address-location cleanup hook, while preserving compatibility behavior from the v0 test.

### Important APIs, Types, And Functions
The file copies v2 definitions for `perf_dlfilter_sample`, `perf_dlfilter_al`, and `perf_dlfilter_fns`. Compared with v0, the sample adds `machine_pid` and `vcpu`, address locations add private data, and the function table adds `al_cleanup()` while reducing reserved slots. The callback functions mirror the v0 test and additionally call `al_cleanup()` when present after `resolve_address()`.

### Control Flow
`start()` parses test arguments and stores expected IP/address values. The early and normal callbacks enforce one-shot ordering, validate sample fields, test `attr()`, and, when configured, resolve IP, data address, arbitrary address, and object code. `stop()` verifies lifecycle and frees state.

### State And Persistence
Only the heap `filter_data` and static lifecycle guard are retained during one plugin run.

### Dependencies And Integration Points
It is consumed by the perf dlfilter API self-test and depends on perf providing a v2-compatible function table but tolerating older optional function absence.

### Risks
As an ABI fixture, field ordering and reserved slot count are sensitive. Accidentally including the live header would stop testing compatibility with the historical v2 layout.

### Test Signals
The perf dlfilter C API test should pass with `al_cleanup()` available or absent, verifying v2 callbacks, struct size checks, symbol resolution, object-code reads, and early filtering behavior.
