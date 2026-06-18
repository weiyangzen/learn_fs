# sources/distributed-fs/ceph-client/sound/usb/6fire/common.h

## Purpose
Provides common includes, prefix macro, and forward declarations for the 6Fire driver.

## Important APIs, Types, and Functions
Defines `PREFIX "6fire: "` and forward declares `sfire_chip`, `midi_runtime`, `pcm_runtime`, `control_runtime`, and `comm_runtime`.

## Control Flow
No executable logic.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Includes Linux slab and USB headers plus ALSA core, making these available to 6fire headers.

## Risks
Header bloat can mask missing includes in implementation files. The prefix is not consistently used across all logged errors.

## Test Signals
Build-only signal: headers should compile independently through the implementation files.
