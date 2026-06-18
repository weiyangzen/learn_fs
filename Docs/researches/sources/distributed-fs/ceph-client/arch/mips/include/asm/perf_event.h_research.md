# sources/distributed-fs/ceph-client/arch/mips/include/asm/perf_event.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/perf_event.h

### Purpose
`perf_event.h` is intentionally empty except for its include guard. It satisfies the generic `linux/perf_event.h` expectation that every architecture provide an `asm/perf_event.h` include point.

### Important APIs, Types, And Functions
There are no exported functions, types, or feature macros beyond `__MIPS_PERF_EVENT_H__`.

### Control Flow
There is no runtime control flow. Inclusion succeeds and leaves generic perf code to use other MIPS PMU support paths.

### State, Persistence, Dependencies, And Integration
No state or persistence exists here. Integration is purely include-time: generic perf headers can include this file on MIPS without conditional special cases.

### Risks
The risk is accidental addition of stale architecture declarations or removal of the file, either of which can break generic perf include contracts.

### Test Signals
Compile MIPS kernels with `CONFIG_PERF_EVENTS` and representative PMU options; include-order failures are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/perf_event.h -->
