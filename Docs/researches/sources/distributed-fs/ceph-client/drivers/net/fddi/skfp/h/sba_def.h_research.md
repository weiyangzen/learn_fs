# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/sba_def.h

## Purpose
`sba_def.h` provides constants for ESS/SBA bandwidth allocation, RAF command inputs, default overhead, payload/path limits, and optional full-SBA states and status values.

## Important APIs, Types, And Functions
Common constants include `PHYS`, `PERM_ADDR`, `SB_STATIC`, `MAX_PAYLOAD`, `PRIMARY_RING`, `UNKNOWN_SYNC_SOURCE`, `REQ_ALLOCATION`, `REPORT_RESP`, `CHANGE_RESP`, `TNEG`, `NIF`, `SB_STOP`, `SB_START`, `REPORT_TIMER`, `CHANGE_REQUIRED`, and `DEFAULT_OV`. Under `SBA`, it defines allocator states, capacities, timers, node/session limits, and deallocation flags.

## Control Flow
There is no code. `ess.c` uses `MAX_PAYLOAD`, `PRIMARY_RING`, and `DEFAULT_OV` to validate and build RAF allocation behavior.

## State And Persistence
No runtime state is declared. Constants define accepted wire/protocol values and allocator bounds.

## Dependencies And Integration Points
Included by `sba.h` and indirectly by `smc.h`/`ess.c`. Values must match the Synchronous Bandwidth Allocation Implementer's Agreement and SMT RAF parameter handling.

## Risks And Edge Cases
`MAX_PAYLOAD` and `DEFAULT_OV` are protocol policy values; changing them can make RAF negotiation incompatible. `PRIMARY_RING` is encoded as a 32-bit value while some RAF fields are swapped specially in `smt.h`.

## Test Signals
ESS allocation bounds, primary-ring filtering, default overhead when static payload is set, zero-payload deallocation, and optional full-SBA state transition tests.
