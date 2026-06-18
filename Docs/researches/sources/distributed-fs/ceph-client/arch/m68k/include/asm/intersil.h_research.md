<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/intersil.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/intersil.h

## Purpose
`intersil.h` describes the Intersil 7170 clock chip used by Sun3 systems.

## Important APIs, Types, and Functions
It defines command bits for oscillator frequency, 12/24-hour mode, run/stop, interrupt enable, normal/test mode, and the 100 Hz mask. `struct intersil_dt` models counter/alarm date-time fields, and `struct intersil_7170` groups counter, alarm, interrupt register, and command register. `intersil_clock` casts `clock_va` to the mapped device, and `intersil_clear()` reads the interrupt register.

## Control Flow, State, and Persistence
There is no function control flow. Hardware state persists in the RTC registers addressed through `clock_va`.

## Dependencies and Integration Points
Sun3 timekeeping, clock interrupt, and RTC code map `clock_va`, program `cmd_reg`, read `counter`, and clear interrupt state through this header.

## Risks
The structs assume exact hardware register ordering and byte-sized accesses. `intersil_clear()` has side effects by acknowledging interrupts. Incorrect mode bits can stop the clock or enter test mode.

## Test Signals
Boot time should be read correctly, periodic clock interrupts should clear, and 24-hour mode should avoid ambiguous hour values. Suspend/reset behavior should preserve expected RTC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/intersil.h -->
