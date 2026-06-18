# sources/distributed-fs/ceph-client/sound/ppc/tumbler_volume.h

## Purpose
`tumbler_volume.h` provides static codec-specific volume conversion tables used by the PowerMac Tumbler/Snapper mixer driver. The arrays map ALSA integer control indices to TAS3001C/TAS3004 register values for master volume, bass, treble, PCM/mixer gains, and Snapper tone controls.

## Important APIs, Types, And Functions
The file has no functions or types. It exports file-local `static const unsigned int` arrays: `master_volume_table`, `treble_volume_table`, `bass_volume_table`, `mixer_volume_table`, `snapper_treble_volume_table`, and `snapper_bass_volume_table`. `tumbler.c` uses `ARRAY_SIZE()` on these tables to define ALSA control limits and then indexes them to build one-, three-, six-, or nine-byte TAS register writes.

## Control Flow
There is no executable flow in this header. Control flow is indirect: ALSA mixer callbacks in `tumbler.c` validate user indices against these array sizes, clamp internal values before hardware writes, translate indices to packed TAS gain/tone values, and send the corresponding bytes over I2C.

## State And Persistence
The arrays are immutable kernel text/rodata. User-visible state is not stored here; persisted mixer state is kept by `struct pmac_tumbler` and translated through the tables each time hardware must be updated or restored after resume.

## Dependencies And Integration Points
This header is included only by `tumbler.c`. The table width and value encoding are tied to TAS3001C/TAS3004 register formats: master and mixer tables are 24-bit values, while tone tables are byte-sized values consumed by the driver according to the target register.

## Risks And Edge Cases
Because ALSA control ranges derive directly from `ARRAY_SIZE()`, changing table length changes the user ABI range for those controls. Incorrect table ordering or values would produce wrong attenuation or tone curves even though control validation still passes. The tables have no self-description, so maintainers must preserve the implicit contract between array index, perceived volume curve, register width, and codec model.

## Test Signals
Tests should check that ALSA control max values match table sizes, boundary indices write valid TAS bytes, mute uses zero rather than table lookup, and suspend/resume or jack automute replays the same register values for selected volume/tone indices.
