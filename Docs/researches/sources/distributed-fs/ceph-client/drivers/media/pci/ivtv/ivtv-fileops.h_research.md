# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-fileops.h

## Purpose
`ivtv-fileops.h` declares the V4L2 file-operation entry points and stream utility functions implemented in `ivtv-fileops.c`.

## Important APIs, Types, and Functions
The header exposes open/read/write/close functions, encoder and decoder poll functions, capture/decode start and stop helpers, mute/unmute helpers, and shared stream claim/release utilities used by ivtv core code and ivtv-alsa.

## Control Flow
No executable control flow lives here. Stream registration code installs these callbacks into video devices, while other modules call claim/release and start/stop helpers to coordinate shared stream ownership.

## State and Persistence
The functions declared here mutate `struct ivtv`, `struct ivtv_stream`, and `struct ivtv_open_id` state, but the header itself stores none.

## Dependencies and Integration Points
It requires Linux file and poll types plus ivtv core structs from `ivtv-driver.h`. It integrates stream registration, file operations, ALSA PCM capture sharing, and driver remove shutdown paths.

## Risks and Edge Cases
The stream claim/release helpers are exported and shared, so callers must obey ivtv locking and stream type rules. Signature drift here affects video device registration and any extension modules.

## Test Signals
Build with ivtv stream registration and ivtv-alsa enabled. Runtime tests should show correct callbacks on every registered V4L2 node and balanced stream claim/release behavior across file and ALSA users.
