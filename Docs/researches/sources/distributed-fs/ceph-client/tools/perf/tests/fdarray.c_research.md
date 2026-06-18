# sources/distributed-fs/ceph-client/tools/perf/tests/fdarray.c

## Purpose
Tests the generic `fdarray` helper used by perf polling code, specifically filtering entries by `revents` masks and automatic growth when adding more descriptors than the initial allocation.

## Important APIs, Types, and Functions
- `fdarray__init_revents()` fills all allocated entries with descending fake fds and uniform `events`/`revents`, while setting `nr = nr_alloc`.
- `fdarray__fprintf_prefix()` prints debug state only when `verbose > 0`.
- `test__fdarray__filter()` verifies `fdarray__filter()` keeps all entries when the filter mask is absent, removes all entries when all match `POLLHUP`, and compacts partial survivors.
- `test__fdarray__add()` uses local `FDA_ADD` and `FDA_CHECK` macros to verify `fdarray__add()` preserves fd/event values and grows from an initial 2 slots to at least 4 entries.

## Control Flow
The filter test creates a 5-entry array with growth step 5, initializes synthetic `revents`, calls `fdarray__filter()` under several masks, and validates resulting `nr` counts. The add test creates a 2-entry array with growth step 2, adds two entries, then adds two more to force reallocation, checking each insertion and final entry values.

## State and Persistence
State is heap-local to `struct fdarray`; the tests allocate with `fdarray__new()` and always delete with `fdarray__delete()` on normal cleanup paths. Debug printing goes to stderr when verbose. No persistent state is produced.

## Dependencies and Integration Points
Integrates with `api/fd/array.h`, `poll.h`, perf debug output, and the tests framework via two `DEFINE_SUITE()` registrations: fdarray filtering and fdarray add/autogrow behavior.

## Risks and Edge Cases
- The tests use fake integer fds and do not interact with actual kernel descriptors.
- The filter callback arguments are `NULL`, so callback-assisted cleanup behavior is not covered.
- The add test checks `events` but its error message labels one path as `revents`; the functional assertion is still on the intended field.

## Test Signals
Passing requires correct compaction counts for all/none/partial filtering and correct order/value preservation across autogrow. Failures print detailed line-numbered diagnostics.
