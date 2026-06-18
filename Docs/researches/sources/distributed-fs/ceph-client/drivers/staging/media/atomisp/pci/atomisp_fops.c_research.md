# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.c

## Purpose
This file implements AtomISP V4L2 file operations and videobuf2 queue operations for the capture node. It owns open/release behavior, buffer setup/mapping/cleanup, and movement of queued video/stat/metadata buffers into CSS.

## Important APIs and Functions
`atomisp_queue_setup()` derives CSS frame info and allocates stat buffers. `atomisp_buf_init()` initializes IA CSS frames and maps vb2 vmalloc memory into HMM. `atomisp_buf_queue()` validates state, handles cache flushing, and queues frames or waits for parameters. `atomisp_qbuffers_to_css()` selects the active CSS pipe. `atomisp_q_video_buffers_to_css()` applies per-frame parameters and enqueues output plus 3A/metadata/DIS side buffers. `atomisp_open()` and `atomisp_release()` implement single-open, runtime PM, sensor power, and CSS teardown.

## Control Flow
Open initializes V4L2 file handle, validates camera presence, rejects a second user, powers the ISP, and resets device/subdevice state. Queue setup ensures CSS frame information exists, using a default format fallback. Buffer init maps memory to CSS. Buffer queue appends frames to active or parameter-waiting lists, then queues to CSS if streaming. Release drains vb2, decrements users, frees CSS/internal buffers, powers down the sensor, destroys CSS streams/pipes, and runtime-suspends the device.

## State and Persistence
State includes pipe user count, `frame_info`, `pix`, vb2 queue, active/in-CSS/waiting lists, per-frame parameter/config arrays, CSS stat buffer lists/counters on `asd`, and device fatal/frequency defaults.

## Dependencies and Integration Points
Depends on V4L2, vb2-vmalloc, HMM, AtomISP command helpers, CSS compatibility, ioctl stream callbacks, and subdev state. CSS event handling later completes frames queued here.

## Risks
Single-open semantics may surprise apps. `wbinvd()` is global and expensive. Per-frame parameter handling is legacy and delicate. CSS queue failures must move frames back correctly. HMM frame data must be freed once in cleanup. Lock ordering between `isp->mutex` and pipe spinlocks is important.

## Test Signals
Open/release with no sensor and double-open, `REQBUFS` before `S_FMT`, buffer init/cleanup leak checks, qbuf/dqbuf with per-frame parameters, CSS queue-depth behavior, side-buffer queueing, and active-buffer release cleanup.
