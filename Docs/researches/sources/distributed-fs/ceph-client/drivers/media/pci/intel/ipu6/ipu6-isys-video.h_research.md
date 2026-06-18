# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.h

## Purpose
This header defines the IPU6 ISYS video-node, firmware-stream, pixel-format, and watermark data structures used by queue, video, and ISYS core code.

## Important APIs, Types, And Data
`IPU6_ISYS_OUTPUT_PINS` is 11, and `IPU6_ISYS_MAX_PARALLEL_SOF` is 2. `struct ipu6_isys_pixelformat` stores V4L2 fourcc, bit depth, packed bit depth, media-bus code, firmware CSS format, and metadata flag. `struct ipu6_isys_stream` mirrors a firmware stream: mutex, sequence counter, recent SOF ring, source/handle, output pin count, owning subdevice, queue counts, streaming state, completions for open/close/start/stop, queue list, output pin to queue map, error, and CSI virtual channel. `struct ipu6_isys_video` owns the vb2 queue, mutex, media pad, video device, current video/meta formats, stream pointer, CSI link, watermark data, source stream, VC, and DT.

## Control Flow
Video nodes use the declarations here to allocate streams, prepare firmware pin configuration, open/close firmware, and query active format parameters for queue sizing. Watermark fields are populated before streaming and linked into the ISYS global watermark list while the stream is active.

## State And Persistence
The structures contain live driver state only. Completions and counters are reset around each firmware command sequence; format state persists until the video device is closed or reconfigured.

## Dependencies And Integration Points
The header depends on media entities, V4L2 devices, completion/mutex/list primitives, and `ipu6-isys-queue.h`. It is the central contract among ISYS video, queue, CSI-2, and ISYS core files.

## Risks And Test Signals
The `output_pins_queue` array is bounded by firmware pin IDs; firmware responses with out-of-range pins must be ignored safely. Tests should cover shared streams, stream refcounting, multiple SOFs before data-ready, and cleanup after failed firmware completions.
