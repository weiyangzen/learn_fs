# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg.h

Purpose: declares the lightweight MJPEG header representation and parser API used by the Delta MJPEG decoder.

Important APIs and types: defines `struct mjpeg_component`, `MJPEG_MAX_COMPONENTS`, `struct mjpeg_header`, and `delta_mjpeg_read_header`.

Control flow: the decoder passes an AU virtual address, size, output header, and data-offset pointer to `delta_mjpeg_read_header` before negotiating stream info or invoking firmware decode.

State and persistence: no owned state. The header structure is stored in `delta_mjpeg_ctx` by the decoder after parsing.

Dependencies and integration points: includes `delta.h` for decoder context types. The parser implementation lives in `delta-mjpeg-hdr.c` and the consumer is `delta-mjpeg-dec.c`.

Risks: `MJPEG_MAX_COMPONENTS` is five, and the parser rejects component counts greater than or equal to that value, so a stream with exactly five components is not accepted despite the array length. The component structure is defined for future detail but current parser does not populate its fields.

Test signals: compile coverage and parser tests using representative MJPEG headers with varying component counts and dimensions.
