# sources/distributed-fs/ceph-client/tools/perf/util/cacheline.h

## sources/distributed-fs/ceph-client/tools/perf/util/cacheline.h

Purpose: this header declares cacheline-size discovery and provides helpers to normalize addresses to cacheline boundaries.

Important APIs: `cacheline_size()` returns the system size. `cl_address(address, double_cl)` returns the base address of the containing cacheline or adjacent-prefetch doubled line. `cl_offset(address, double_cl)` returns the offset within that line.

Control flow and state: helpers call `cacheline_size()`, optionally double it, then mask the address. State is held by `cacheline_size()` implementation.

Dependencies and integration: used by perf c2c/memory reporting code to bucket addresses. Includes Linux compiler attributes.

Risks: helpers assume `cacheline_size()` returns a power-of-two positive value. A zero or non-power-of-two size produces invalid masks. `double_cl` models adjacent cacheline prefetch but may not match every architecture.

Test signals: unit-test address/offset outputs for 64-byte and doubled 128-byte lines, and behavior when discovery fails.
