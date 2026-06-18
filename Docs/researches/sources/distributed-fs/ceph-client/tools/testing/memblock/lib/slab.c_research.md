<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/lib/slab.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/lib/slab.c

## Purpose

`lib/slab.c` provides the tiny slab-availability hook needed by kernel code compiled into the memblock simulator.

## Important APIs, Types, and Functions

It defines global `enum slab_state slab_state` and implements `slab_is_available()` as `slab_state >= UP`.

## Control Flow

The only control flow is the comparison against the `UP` slab state. Callers can treat allocation helpers as available only after the simulated slab state reaches that level.

## State and Persistence Behavior

`slab_state` is process-global simulator state. It is not persisted beyond a test process and is reset only by normal process startup or explicit test code.

## Dependencies and Integration Points

It includes `<linux/slab.h>` from the tool/kernel header set and links with memblock code paths that test slab availability.

## Risks and Edge Cases

The implementation does not model slab allocation itself. Any kernel code that needs real slab caches would require additional simulator support.

## Test Signals

Build/link success and paths that query `slab_is_available()` are the relevant signals. Tests should continue to pass with the default `slab_state` expected by the simulator harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/lib/slab.c -->
