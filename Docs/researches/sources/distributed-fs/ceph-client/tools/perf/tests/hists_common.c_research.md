# sources/distributed-fs/ceph-client/tools/perf/tests/hists_common.c

## Purpose
Provides shared synthetic machine, thread, mmap, DSO, and symbol fixtures plus histogram debug printers used by multiple histogram tests.

## Important APIs, Types, and Functions
- Static fixture arrays define fake threads (`perf` pids 100/200 and `bash` pid 300), fake mmap regions for executable/libc/kernel DSOs, and fake symbols for each DSO.
- `struct fake_sym` captures symbol start, length, and name.
- `setup_fake_machine(struct machines *machines)` creates or finds the host machine, creates threads, processes synthetic mmap events, marks DSOs loaded, and inserts symbols into each DSO symbol tree.
- `print_hists_in()` prints input or collapsed rb-tree entries, depending on `hists__has(hists, need_collapse)`.
- `print_hists_out()` prints output rb-tree entries with period and accumulated period.

## Control Flow
`setup_fake_machine()` first obtains the host machine. It then creates threads and sets their comm strings. Next it synthesizes mmap events for each pid and DSO using `machine__process_mmap_event()`. Finally it iterates DSO symbol definitions, obtains/creates each DSO, marks it loaded, allocates symbols with `symbol__new()`, and inserts them into the DSO's symbol collection. On allocation failure it deletes created threads and returns `NULL`.

## State and Persistence
The function mutates the supplied `struct machines` hierarchy by adding threads, maps, DSOs, and symbols. All state is in-memory and expected to be released by callers through `machines__exit()` and per-test map/thread puts. No files are read or written.

## Dependencies and Integration Points
This fixture is consumed by `hists_filter.c`, `hists_link.c`, `hists_cumulate.c`, and `hists_output.c`. It integrates with perf machine/thread/map/DSO/symbol processing and sort/hist data structures.

## Risks and Edge Cases
- Synthetic kernel mappings are represented via mmap events with `PERF_RECORD_MISC_USER` sample cpumode, which is adequate for tests but not a full kernel event simulation.
- Fixture correctness depends on address macros from `hists_common.h` remaining aligned with fake symbol offsets.
- The debug printers assume entries have valid maps and symbols.

## Test Signals
The file does not define a suite itself. Its signal is indirect: downstream histogram tests fail if synthetic resolution cannot find expected comm/DSO/symbol combinations or if the fixture cannot be allocated.
