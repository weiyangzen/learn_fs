# Research: sources/distributed-fs/openafs/src/rx/rx_clock.h

## sources/distributed-fs/openafs/src/rx/rx_clock.h

### Purpose
`rx_clock.h` defines RX's `struct clock`, time-source selection, and arithmetic/comparison macros used throughout event scheduling, retransmission, RTT calculation, and RPC statistics.

### Important APIs and Macros
- Defines `struct clock { afs_int32 sec; afs_int32 usec; }`.
- Selects `clock_Init`, `clock_NewTime`, `clock_UpdateTime`, `clock_GetTime`, and `clock_Sec` implementations for kernel, pthread/gettimeofday/UKERNEL, or interval-timer backends.
- Provides `clock_ElapsedTime`, comparison macros (`clock_Gt`, `clock_Ge`, `clock_Eq`, `clock_Le`, `clock_Lt`), zeroing/testing, add/subtract, millisecond conversion macros, and `clock_AddSq` for square accumulation in statistics.

### Control Flow and State
Most behavior is macro-expanded at call sites. Non-kernel pthread/gettimeofday paths read wall time directly. Kernel paths call `osi_GetTime`/`osi_Time`. Legacy non-pthread user-space paths use cached `clock_now` from `rx_clock.c`, invalidated by `clock_NewTime`.

### Dependencies and Integration Points
This header is used by `rx_event.c`, `rx.c`, `rx_call.c`, `rx_globals.h`, RPC stats, and any timeout code. It depends on platform time headers, `afs/afs_osi.h` in kernel builds, and `afs/afsutil.h` on Windows.

### Risks and Edge Cases
- Some macros assume non-negative durations and normalized microseconds.
- `clock_Sub` assumes the second operand is not greater than the first.
- `clock_Float` returns seconds plus a double expression but can surprise callers if integer conversions are introduced.
- The wall-time paths can move backwards after system clock changes; `rx_event.c` compensates for timer scheduling.

### Test Signals
Unit tests for arithmetic normalization, subtraction borrow behavior, elapsed milliseconds, square accumulation, and scheduler behavior after backward clock jumps are high-value.
