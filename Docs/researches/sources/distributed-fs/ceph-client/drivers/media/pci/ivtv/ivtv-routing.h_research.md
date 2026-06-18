# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-routing.h

## Purpose
This header declares the ivtv audio/video routing helpers.

## Important APIs, Types, and Functions
It declares `ivtv_audio_set_io(struct ivtv *itv)` and `ivtv_video_set_io(struct ivtv *itv)`.

## Control Flow
There is no executable logic. Input and audio ioctl handlers call these functions after updating `struct ivtv` selection state.

## State and Persistence Behavior
The header stores no state. The implementation programs persistent hardware routing in V4L2 subdevices and board-specific GPIO/mux chips.

## Dependencies and Integration Points
It depends on `struct ivtv` and is included by ioctl and other modules that need to reapply routing after state changes.

## Risks
The function signatures provide no locking contract; callers must serialize routing changes with active-stream restrictions in the ioctl layer.

## Test Signals
Build coverage and runtime input/audio switching across supported board profiles validate this interface.
