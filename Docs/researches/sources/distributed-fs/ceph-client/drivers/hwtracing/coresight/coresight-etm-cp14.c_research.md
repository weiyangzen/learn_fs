# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm-cp14.c

## Purpose
`coresight-etm-cp14.c` provides ETM register read/write access through ARM CP14 coprocessor instructions for ETM implementations accessed via CP14 rather than MMIO.

## Important APIs, Types, And Functions
The file exports `etm_readl_cp14(u32 reg, unsigned int *val)` and `etm_writel_cp14(u32 reg, u32 val)`. Both are large switch statements mapping logical ETM register offsets/macros from `coresight-etm.h` to architecture-specific `etm_read()` and `etm_write()` CP14 register identifiers from `asm/hardware/cp14.h`.

Read coverage includes control, configuration, trigger, status, trace enable, FIFO, address comparators, access type registers, counters, sequencer events, external outputs, context ID comparators, implementation-specific registers, sync, ID, external input selection, timestamp, aux, trace ID, VMID, OS lock/status, and powerdown registers. Write coverage is similar but limited to writable registers and returns `-EINVAL` for unsupported offsets.

## Control Flow
Callers pass a logical ETM register offset. The switch selects the corresponding CP14 register access and returns 0 on success. Unknown offsets set read output to 0 and return `-EINVAL`, or return `-EINVAL` for writes without touching hardware.

## State And Persistence
There is no software state in this file. All state is in the ETM hardware registers reached by CP14 accesses. Writes persist according to ETM hardware and CPU debug power behavior.

## Dependencies And Integration Points
The file depends on ARM CP14 accessors and ETM register macro definitions. It is an access backend used by ETM driver code that abstracts register I/O across MMIO and CP14 implementations.

## Risks
The switch tables must stay synchronized with ETM register definitions and CP14 architectural register names. Missing writable cases can make higher-level ETM programming fail with `-EINVAL`; incorrectly writable cases can write read-only or unsafe registers. CP14 access is architecture-specific and generally relevant to older ARM/ETM designs.

## Test Signals
Compile tests on supported ARM configurations are the first signal. Runtime tests should read known ID/config registers through CP14, write/read back safe programmable registers, and verify unsupported offsets return `-EINVAL` without side effects. Higher-level ETM enable tests indirectly validate the mapping completeness.
