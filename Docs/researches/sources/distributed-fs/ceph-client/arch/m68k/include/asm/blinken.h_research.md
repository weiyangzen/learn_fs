<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/blinken.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/blinken.h

## Purpose
This header provides HP300 front-panel LED support for m68k "blinkenlights" diagnostics.

## Important APIs, Types, And Functions
- `HP300_LEDS` is the LED I/O address.
- `hp300_ledstate` is the software shadow byte.
- `blinken_leds(int on, int off)` updates the shadow and writes the inverted value with `out_8()` when `MACH_IS_HP300`.

## Control Flow
Callers request bits to turn on and off. The inline helper ignores non-HP300 machines, updates `hp300_ledstate`, and writes the hardware register.

## State And Persistence Behavior
Persistent state is the global `hp300_ledstate` shadow plus the LED hardware latch. The function is not synchronized, so concurrent updates can race.

## Dependencies And Integration Points
It depends on machine detection from `asm/setup.h` and I/O accessors from `asm/io.h`. It integrates with HP300 platform diagnostics and activity indicators.

## Risks And Edge Cases
The hardware uses inverted output, so direct writes must preserve that convention. Unsynchronized read-modify-write on `hp300_ledstate` can lose concurrent bit changes.

## Test Signals
On HP300 hardware, calls that set and clear individual LED bits should update the panel correctly. Non-HP300 builds should compile and perform no I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/blinken.h -->
