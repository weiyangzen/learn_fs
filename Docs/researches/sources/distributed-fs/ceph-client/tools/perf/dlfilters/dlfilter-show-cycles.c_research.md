# sources/distributed-fs/ceph-client/tools/perf/dlfilters/dlfilter-show-cycles.c

### Purpose
This sample `perf script --dlfilter` plugin prints cumulative cycle counts and deltas at the start of each output line, using IPC-derived `cyc_cnt` fields.

### Important APIs, Types, And Functions
It uses the public `perf_dlfilter.h` ABI. `filter_event_early()` accumulates counts before normal script filtering. `filter_event()` prints totals and deltas. `filter_description()` exposes help text. Counts are stored per CPU in `cycles[MAX_CPU][MAX_ENTRY]` or per TID in an open-addressed hash table when CPU is not recorded.

### Control Flow
`event_entry()` classifies event names into instructions, branches, or other. Early filtering adds `sample->cyc_cnt` to the relevant bucket. Later filtering prints the current total and the difference from the last reported value, then updates the reported snapshot.

### State And Persistence
All state is static process memory: per-CPU arrays, per-TID table, and report snapshots. It is reset on each plugin load and not persisted.

### Dependencies And Integration Points
The plugin is loaded by perf's dlfilter mechanism and relies on `perf_dlfilter_sample.event`, `cpu`, `tid`, and `cyc_cnt` being populated by perf script.

### Risks
`MAX_CPU` is fixed at 4096; higher CPU ids fall back only if TID is present. The TID hash table caps at half full and has no deletion. Event classification is prefix based, so renamed events may fall into `OTHER_CYC`.

### Test Signals
Run `perf script --dlfilter dlfilter-show-cycles.so` on perf.data with IPC fields and verify per-line totals/deltas for branch, instruction, and other events, including data without CPU but with TID.
