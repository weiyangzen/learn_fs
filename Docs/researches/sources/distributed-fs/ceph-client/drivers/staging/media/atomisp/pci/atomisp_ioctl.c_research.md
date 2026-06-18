# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.c

## Purpose
This file implements the AtomISP V4L2 ioctl table, output format mapping, input selection, frame/format enumeration, controls, qbuf/dqbuf wrappers, and streaming start/stop orchestration.

## Important APIs and Functions
`atomisp_output_fmts[]` maps V4L2 formats to IA CSS frame formats. `atomisp_pipe_check()` rejects fatal-error and busy settings-change paths. Standard ioctl handlers cover querycap, input, frame size/interval, formats, controls, buffers, streamon/off, and stream parameters. `atomisp_alloc_css_stat_bufs()` allocates 3A/DIS/metadata buffers. `atomisp_qbuf_wrapper()` and `atomisp_dqbuf_wrapper()` preserve legacy per-frame/exposure IDs. `atomisp_start_streaming()` and `atomisp_stop_streaming()` drive runtime streaming.

## Control Flow
Format and frame enumeration consult the current sensor and AtomISP format tables. `S_INPUT` selects a sensor only when the pipe is not busy. `S_PARM` forwards frame interval or changes run mode. Stream start validates state, repairs links, starts the media pipeline, configures DMA burst, flushes caches, applies CSS parameters, starts CSS, marks streaming, queues buffers, enables SOF IRQs, configures CSI2, switches DFS, sets CSI-ready, and starts the sensor. Stop clears streaming, disables IRQs, stops CSS, drains events, stops sensor, lowers DFS, resets ISP, flushes buffers, recreates streams, and stops the media pipeline.

## State and Persistence
Mutates pipe pixel format and legacy config arrays, `asd->input_curr`, run mode, high-speed mode, CSS params, streaming flag, sequence counters, exposure IDs, and saved PCI register values used for workarounds.

## Dependencies and Integration Points
Depends on V4L2 ioctl/event APIs, PCI config access, AtomISP command helpers, file ops, internal state, CSS compatibility, CSI2 configuration, and sensor subdev calls.

## Risks
`atomisp_vidioc_default()` returns `-EINVAL` for any nonzero private ioctl before its legacy switch, so private AtomISP ioctls are effectively disabled. Legacy `reserved/reserved2` buffer fields are fragile. Stream start has many side effects and rollback requirements. Global cache flushes are expensive. Media pipeline, CSS, sensor, and vb2 states must remain consistent on errors.

## Test Signals
Run v4l2-compliance, enumerate formats/sizes/intervals, exercise `S_INPUT` while streaming, qbuf/dqbuf legacy IDs, stream start/stop/restart, sensor-start rollback, CSI-ready bit handling, DFS transitions, and private ioctl rejection.
