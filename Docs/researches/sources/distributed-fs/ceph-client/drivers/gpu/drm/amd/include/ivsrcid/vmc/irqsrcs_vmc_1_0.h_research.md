# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vmc/irqsrcs_vmc_1_0.h

## Purpose
Defines VMC 1.0 and UTCL2 1.0 source IDs for GPU virtual memory faults and retry events.

## Important APIs, Types, and Functions
No functions or structs are present. VMC macros define VM fault `0`, VM retry `1`, VM context0 all `256`, and VM context1 all `257`. UTCL2 macros define fault `0` and retry `1`.

## Control Flow
The header has no direct control flow. GPUVM and KFD fault handlers use these IDs to distinguish fault, retry, and context-wide VM events.

## State and Persistence
There is no state. The constants persist as hardware source identifiers in fault decode paths.

## Dependencies and Integration Points
The file depends only on its guard. Integration points include GMC/VMC interrupt setup, UTCL2 retry handling, KFD VM fault events, GPUVM diagnostics, and user-visible fault reporting.

## Risks and Test Signals
Wrong mapping can break page fault attribution or retry behavior. Test signals include invalid GPUVA access, retry-capable memory faults, context fault decode, and KFD event delivery.
