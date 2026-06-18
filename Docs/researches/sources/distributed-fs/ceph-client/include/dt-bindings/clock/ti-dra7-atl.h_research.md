# sources/distributed-fs/ceph-client/include/dt-bindings/clock/ti-dra7-atl.h

## Purpose
Defines DRA7 ATL word-select input IDs used by the TI ATL clock/audio binding. These values identify McASP frame-sync, AHCLK, external reference, and oscillator sources.

## Important APIs, Types, and Constants
Exports `DRA7_ATL_WS_*` macros from `DRA7_ATL_WS_MCASP1_FSR` 0 to `DRA7_ATL_WS_OSC1_X1` 15. The constants enumerate selectable word-select sources rather than clocks in a broad SoC clock tree.

## Control Flow and State
No runtime logic. ATL clock muxing and audio synchronization state are controlled by the TI ATL driver and hardware.

## Dependencies and Integration Points
Self-contained DT binding included by DRA7 audio clock nodes and consumers that select ATL word-select sources.

## Risks and Test Signals
Wrong values can select the wrong audio sync source and cause clocking or sample-rate failures. Test signals include DT schema validation and audio playback/capture tests across McASP and external reference configurations.
