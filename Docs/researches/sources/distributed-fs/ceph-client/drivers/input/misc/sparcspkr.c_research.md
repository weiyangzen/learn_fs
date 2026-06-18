# sources/distributed-fs/ceph-client/drivers/input/misc/sparcspkr.c

## Purpose
`sparcspkr.c` provides input `EV_SND` beeper support for SPARC BBC and Grover speaker hardware. It registers platform drivers for two OF-compatible beeper blocks and maps bell/tone events to hardware timer/counter registers.

## Important APIs, Types, and Functions
`struct sparcspkr_state` holds input device, lock, event callback, and BBC/Grover hardware info. `bbc_count_to_reg()` maps PIT-style counts to BBC register codes. `bbc_spkr_event()` and `grover_spkr_event()` program their respective hardware. `sparcspkr_probe()` allocates/registers the shared input device. `bbc_beep_probe()` and `grover_beep_probe()` map OF resources and call the shared probe. Remove/shutdown functions turn the speaker off and unmap resources.

## Control Flow
Module init registers both platform drivers. The BBC probe reads root `clock-frequency`, maps one register range, and registers `Sparc BBC Speaker`. The Grover probe maps frequency and enable registers and registers `Sparc Grover Speaker`. Input sound events accept `SND_BELL` and `SND_TONE`, normalize bell to 1000 Hz, convert valid frequencies to counts, and under a spinlock either enable/program the speaker or disable it. Shutdown and remove force a zero bell event.

## State and Persistence Behavior
Runtime state is the mapped I/O pointers, input device pointer, event callback, and spinlock. Hardware timer/enable registers persist until programmed off or platform shutdown. No frequency state is cached beyond the hardware registers.

## Dependencies and Integration Points
The driver depends on SPARC OF platform devices, SBUS I/O accessors, input sound events, and OF resource mapping. Compatible strings are `SUNW,bbc-beep` and `SUNW,smbus-beep`.

## Risks and Edge Cases
Frequency values outside 21 to 32766 Hz are treated as off. BBC count conversion clamps low/high ranges to fixed codes. Register programming is low-level and architecture-specific; wrong resource indexes on Grover fail or program the wrong device. Probe uses non-devm input allocation and must explicitly unregister/free on all paths.

## Test Signals
Build and boot tests on BBC and Grover systems, bell and tone events across valid/invalid frequency ranges, remove/shutdown muting, OF resource mapping failures, and concurrent sound events under the spinlock.
