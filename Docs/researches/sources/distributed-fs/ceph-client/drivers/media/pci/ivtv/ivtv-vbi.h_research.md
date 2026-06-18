# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.h

## Purpose
This header declares ivtv VBI input, conversion, output, and deferred-work helpers.

## Important APIs, Types, and Functions
It declares `ivtv_write_vbi_from_user`, `ivtv_process_vbi_data`, `ivtv_used_line`, `ivtv_disable_cc`, `ivtv_set_vbi`, and `ivtv_vbi_work_handler`.

## Control Flow
There is no executable logic. File write paths, IRQ completion, stream setup, and deferred IRQ work call these helpers to process or emit VBI data.

## State and Persistence Behavior
The header stores no state. The implementation mutates VBI buffers, payload queues, frame counters, update flags, and video-output subdevice state.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_buffer`, V4L2 sliced VBI data, and stream type IDs. It bridges fileops, IRQ, ioctl, and stream lifecycle modules.

## Risks
Declared functions are used across sleepable and deferred contexts; callers must choose the right context and locking because the header does not enforce it.

## Test Signals
Build coverage and end-to-end raw/sliced VBI capture, MPEG insertion/reinsertion, VBI output, and passthrough tests validate the interface.
