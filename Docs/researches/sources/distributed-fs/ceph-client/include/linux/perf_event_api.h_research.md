<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event_api.h -->
# sources/distributed-fs/ceph-client/include/linux/perf_event_api.h

## Purpose
Acts as a compatibility/include shim that simply includes `<linux/perf_event.h>`.

## Important APIs, Types, And Functions
- No new types or functions are defined.
- Re-exports the full kernel perf event interface by including `linux/perf_event.h`.

## Control Flow
There is no control flow. Inclusion of this header causes the compiler to parse the perf event API declarations and inline helpers from `perf_event.h`.

## State And Persistence
No independent state is introduced. All state comes from the included perf event core header.

## Dependencies And Integration Points
The integration point is source compatibility for code that includes `linux/perf_event_api.h` instead of `linux/perf_event.h`.

## Risks And Edge Cases
Risk is limited to include-order or dependency churn if `perf_event.h` changes. Any consumer expecting a smaller or different API surface still receives the entire perf event header.

## Test Signals
Build coverage of consumers that include this shim is sufficient. Changes should preserve that include path and verify no circular include or missing dependency appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf_event_api.h -->
