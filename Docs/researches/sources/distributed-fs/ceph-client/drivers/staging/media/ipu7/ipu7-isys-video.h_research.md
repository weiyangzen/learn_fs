# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-video.h

## Purpose
Declares capture video-node state, firmware stream state, pixel-format descriptors, output-pin callbacks, and public video/firmware stream APIs for IPU7 ISYS.

## Important APIs, Types, and Constants
`IPU_INSYS_OUTPUT_PINS` is 11 and `IPU_ISYS_MAX_PARALLEL_SOF` is 2. `struct ipu7_isys_pixelformat` maps V4L2 pixel formats to bit depth, packed depth, media-bus code, and firmware frame format. `struct ipu7_isys_stream` models one firmware stream/CSI virtual channel with mutex, source entity, sequence and buffer counters, SOF timestamp ring, stream source/handle, output pins, queue counts, completions, parent pointer, error code, and VC. `struct ipu7_isys_video` wraps queue, mutex, media pad, video device, current pix format, parent ISYS, CSI2 receiver, stream pointer, streaming flag, VC, and DT.

## Control Flow and State
The header defines the shared state used by queue and video implementation. Queues call into video APIs to prepare streams and change streaming state; firmware ISRs use query helpers to find streams by handle or source/VC; pin-ready callbacks complete buffers. Sequence state and completion objects are long-lived per stream and reused across stream commands.

## Dependencies and Integration Points
Includes media entity and V4L2 device headers plus `ipu7-isys-queue.h`. It bridges `ipu7-isys.c`, `ipu7-isys-queue.c`, `ipu7-isys-video.c`, and CSI2 code. The firmware ABI defines concrete stream config, response, and format values consumed by these declarations.

## Risks and Test Signals
The SOF ring has only two entries, so high parallelism or delayed buffer-ready responses can fall back to current sequence. `output_pins` must be sized to firmware pin IDs and guarded in ISR. Tests should watch sequence/timestamp correctness under multiple in-flight frames, stream refcount lifetime, output pin index bounds, and cleanup of completion waiters during stream errors.
