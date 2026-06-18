# sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-tsl.c

## Purpose
Defines SAA7146 Time Slot List bit constants and two eight-entry TSL programs for Audiowerk audio routing/timing.

## Important APIs, Types, And Functions
Bit macros encode word-select outputs, A1/A2 disable/data-width/bit-select/frame/last-frame/data-output-delay/low/EOS fields. `tsl1[8]` programs analog/digital input and analog/digital output timing for A1, and `tsl2[8]` programs A2 output timing.

## Control Flow
No functions. `aw2-saa7146.c` includes this file and writes `tsl1[i]` to `TSL1 + i*4` and `tsl2[i]` to `TSL2 + i*4` during setup.

## State And Persistence
Static const arrays are immutable module data. Runtime hardware TSL registers are volatile and loaded on setup.

## Dependencies And Integration Points
Integrated by textual inclusion into `aw2-saa7146.c`; it relies on SAA7146 register definitions from the including file context for where arrays are written.

## Risks
The comments mention Audiowerk8 setup while this driver targets Audiowerk2, implying reused timing knowledge. TSL values are low-level hardware timing data; small mistakes can produce channel swaps, silence, or corrupted I2S timing.

## Test Signals
Audio channel mapping is the key signal: analog and digital playback/capture should use the expected left/right slots at 44.1 kHz, with no word-select phase errors or channel swaps.
