# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/trace.h

## Purpose
`trace.h` defines ftrace tracepoints for CODA VPU activity. It instruments firmware command submission/completion and buffer lifecycle points so developers can inspect decode, encode, JPEG, and bitstream FIFO behavior without adding ad hoc logging.

## Important APIs and Events
The file declares `TRACE_SYSTEM coda` and includes `linux/tracepoint.h`, `videobuf2-v4l2.h`, and `coda.h`. Direct events include `coda_bit_run` and `coda_bit_done`. Event classes reduce duplication for buffer events (`coda_buf_class`), buffer plus bitstream metadata events (`coda_buf_meta_class`), and metadata-only decoder events (`coda_meta_class`). Concrete events include `coda_enc_pic_run`, `coda_enc_pic_done`, `coda_bit_queue`, `coda_dec_pic_run`, `coda_dec_pic_done`, `coda_dec_rot_done`, `coda_jpeg_run`, and `coda_jpeg_done`.

## Control Flow and Integration
Call sites invoke generated `trace_coda_*` helpers around command and buffer transitions. The trace entries capture video-device minor, CODA context id, buffer index, command id, and ring-buffer metadata masked by `ctx->bitstream_fifo.kfifo.mask`. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct `trace/define_trace.h` to generate the event implementation from this header.

## State and Persistence
Tracepoints do not own device state. They sample live `struct coda_ctx`, `vb2_v4l2_buffer`, and `coda_buffer_meta` fields at the event point. Persistent output is external to the driver through ftrace/perf buffers when tracing is enabled.

## Dependencies and Risks
The header depends on stable `struct coda_ctx` fields (`fh.vdev`, `idx`, `bitstream_fifo`) and metadata layout. Risks include dereferencing context fields from poorly placed trace calls, misleading masked ring offsets if FIFO sizing changes, and build failures if the include path no longer matches the source tree.

## Test Signals
Build with tracing enabled, run decode/encode/JPEG workloads with `trace-cmd` or ftrace events enabled, and verify event ordering around bit commands, queued buffers, picture run/done, rotation done, and JPEG run/done. Tests should also compile with `TRACE_HEADER_MULTI_READ` behavior.
