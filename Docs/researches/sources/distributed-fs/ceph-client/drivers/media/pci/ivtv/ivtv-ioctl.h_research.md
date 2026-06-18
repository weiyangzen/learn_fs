# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-ioctl.h

## Purpose
This header exposes the ivtv ioctl helper interface shared by stream setup, VBI handling, routing, controls, and other ivtv modules.

## Important APIs, Types, and Functions
It forward-declares `struct ivtv` and declares helpers for VBI service conversion and expansion, OSD alpha programming, decoder speed changes, installation of V4L2 ioctl ops, encoder/decoder standard programming, tuner frequency changes, and input selection.

## Control Flow
There is no executable flow in the header. It allows callers to invoke the implementation in `ivtv-ioctl.c` without pulling in that file's private ioctl dispatch table.

## State and Persistence Behavior
The header stores no state. The declared functions mutate `struct ivtv` state, V4L2 video-device ioctl hooks, firmware OSD state, tuner routing, standard flags, and stream dimensions in the implementation.

## Dependencies and Integration Points
It depends on V4L2 types such as `struct v4l2_sliced_vbi_format`, `struct video_device`, `v4l2_std_id`, `struct v4l2_frequency`, and `struct ivtv_stream`. Consumers include stream registration, VBI conversion, and driver init code.

## Risks
Signature drift would break cross-file ivtv integration. Callers must respect the implementation's locking and active-stream restrictions because the prototypes do not encode those requirements.

## Test Signals
Build coverage catches declaration mismatches. Runtime signals come from ioctl paths that call the declared helpers: stream registration, standard switching, input/frequency switching, speed control, and VBI format expansion.
