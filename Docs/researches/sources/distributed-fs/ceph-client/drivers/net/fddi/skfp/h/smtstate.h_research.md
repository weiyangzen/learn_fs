# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smtstate.h

## Purpose
`smtstate.h` defines SMT state constants for PCM, port modes/types, CFM, ECM, and RMT when not building kernel internals, plus compact snapshot structures for reporting PCM state.

## Important APIs, Types, And Functions
Constants include `PC0_OFF` through `PC9_MAINT`, `PM_*`, `TA`/`TB`/`TS`/`TM`/`TNONE`, CFM states (`SC0_ISOLATED`, `SC4_THRU_A`, etc.), ECM states (`EC0_OUT` through `EC7_DEINSERT`), and RMT states (`RM0_ISOLATED` through `RM7_TRACE`). Runtime report types are `struct pcm_state` and `struct smt_state`.

## Control Flow
No executable code is present. CFM and ECM include it with `KERNEL` defined, so they rely on `cmtdef.h` values instead of duplicate non-kernel constants. State-reporting code uses `struct smt_state` snapshots.

## State And Persistence
The structs are transient snapshots of PCM state for all PHYs: type, state, mode, neighbor, flags, line-state receive value, and signaling bits. Numeric constants are externally meaningful state IDs.

## Dependencies And Integration Points
It depends on `NUMPHYS` from `cmtdef.h` when declaring `struct smt_state`. Included by `cmtdef.h` and state-machine/reporting code.

## Risks And Edge Cases
Duplicate state constants must stay aligned with `cmtdef.h` and SMT MIB values. `KERNEL` changes which constants are visible, so include order matters. `struct pcm_state` uses narrow fields and can truncate if future values exceed current ranges.

## Test Signals
Build with and without `KERNEL`, PCM snapshot generation, state-name mapping in CFM/ECM/RMT/PCM diagnostics, and MIB/report consumers expecting standard numeric state values.
