# sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.h

## Purpose
Defines Hoontech/STAudio/Event device IDs, the exported card table, and GPIO bit-manipulation macros for DSP24 external box control and DSP24 Value AK4524 access.

## Important APIs, Types, and Functions
`HOONTECH_DEVICE_DESC` contributes supported-device text. `ICE1712_SUBDEVICE_STDSP24`, `STDSP24_VALUE`, `STDSP24_MEDIA7_1`, `EVENT_EZ8`, and `STAUDIO_ADCIII` identify real and dummy model-selected boards. The header declares `snd_ice1712_hoontech_cards[]`. Macros such as `ICE1712_STDSP24_0_BOX()`, `ICE1712_STDSP24_1_CHN1()`, `ICE1712_STDSP24_2_MIDIIN()`, `ICE1712_STDSP24_3_MUTE()`, `ICE1712_STDSP24_SET_ADDR()`, and `ICE1712_STDSP24_CLOCK()` mutate the four-byte box image used by `hoontech.c`. Config flags describe global and per-box channel/MIDI enables.

## Control Flow
No code executes in the header. The macros are invoked by `hoontech.c` during initialization and GPIO sequencing to build byte values before clocking them into external hardware.

## State and Persistence Behavior
The macros mutate an in-memory byte array, usually `hoontech_spec.boxbits`. Persistence is limited to runtime memory and external latch state. Dummy subdevice IDs depend on explicit model selection because some hardware shares subsystem IDs.

## Dependencies and Integration Points
Included by `hoontech.c` and indirectly by `ice1712.c` board-table aggregation. The AK4524 GPIO masks integrate with the shared AK4xxx initialization helper.

## Risks
The macros directly assign expressions into array slots and evaluate the array argument multiple times, so callers must pass a stable lvalue array. Bit packing is hardware-specific and opaque; off-by-one address or channel bits can route the wrong external box channel or MIDI path. Dummy IDs require careful model matching to avoid misidentification.

## Test Signals
Compile macro users, force each Hoontech model path, inspect `boxbits` during initialization, verify external box channel/MIDI routing, and confirm DSP24 Value AK4524 serial masks select the intended GPIO pins.
