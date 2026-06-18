<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uprobe_multi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uprobe_multi.c

## Purpose
`uprobe_multi.c` is a target executable for uprobe_multi and USDT tests. It defines one weak `uprobe()` function, many generated weak functions for bulk multi-uprobe attachment, many USDT probes for stress testing, and build-ID residency triggers.

## Important APIs, Types, And Functions
- Macro families `F10`, `F100`, `F1000`, and `F10000` generate definitions and calls for large numbers of weak functions.
- `bench()` calls 50,000 generated functions to trigger attached uprobes.
- `usdt()` fires 50,000 `STAP_PROBE(test, usdt)` probes.
- `trigger_uprobe(bool build_id_resident)` uses `madvise(MADV_POPULATE_READ/MADV_PAGEOUT)`, `mincore()`, and `uprobe()` to test build-ID page resident and paged-out cases.
- `main()` dispatches `bench`, `usdt`, `uprobe-paged-out`, and `uprobe-paged-in`.

## Control Flow
The selected mode runs one of the generated trigger loops or build-ID preparation path. For paged-out mode, it page-aligns `build_id_start`, populates it, repeatedly attempts to page it out and checks residency with `mincore()`, then calls `uprobe()`. Invalid arguments print usage and return `-1`.

## State And Persistence
State is limited to executable text, build-id mapped pages, and generated weak symbols. `madvise()` changes page residency but not persistent data.

## Dependencies And Integration Points
It depends on `<sdt.h>`, linker-provided `build_id_start`/`build_id_end`, Linux `madvise` constants, and BPF tests that attach uprobes/USDT probes to this executable.

## Risks And Edge Cases
The generated symbol count is huge and affects compile/link time and binary size. `MADV_PAGEOUT` is best-effort; the loop may not evict the page within 500 attempts. Usage text omits the paged-in/paged-out modes even though they are supported. Weak symbols can be overridden by link context.

## Test Signals
Consumers expect mode exit status zero and BPF-side counters matching the number of triggered functions/probes or one `uprobe()` call. Build-ID tests distinguish successful attach when build-id memory is resident versus paged out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/uprobe_multi.c -->
