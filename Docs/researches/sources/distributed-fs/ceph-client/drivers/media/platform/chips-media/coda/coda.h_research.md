# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda.h

`coda.h` is the private shared contract for the CODA V4L2 mem2mem driver. It defines product IDs, device-type metadata, device/context state structures, codec and queue metadata, parameter/control storage, buffer metadata, IRAM allocation state, context operation callbacks, debug helpers, and cross-file prototypes.

Important structures are `struct coda_devtype`, `struct coda_aux_buf`, `struct coda_dev`, `struct coda_codec`, `struct coda_params`, `struct coda_buffer_meta`, `struct coda_q_data`, `struct coda_iram_info`, `struct coda_context_ops`, `struct coda_internal_frame`, and `struct coda_ctx`. The header also declares GDI map constants, `V4L2_CID_CODA_MB_ERR_CNT`, register access helpers, queue initialization, firmware checking, bitstream helpers, codec helpers, JPEG helpers, operation tables, and IRQ handlers.

Control flow is shaped by `struct coda_context_ops`: common mem2mem code selects an ops table per video node, initializes queues, starts streaming, prepares picture runs, completes or times out runs, runs sequence init/end workers, and releases context-private buffers. Helper prototypes connect codec-specific parsers and hardware programming modules into the generic V4L2 flow.

Runtime persistence lives in `struct coda_dev` and `struct coda_ctx`: firmware buffers, clocks/reset/MMIO, IRAM/work/temp/code buffers, m2m device, locks, debugfs, VDOA, vb2/mem2mem context, control state, bitstream FIFO, metadata list, internal frame buffers, and sequence counters. The header itself stores no data.

Dependencies include Linux debugfs, IDA, IRQ, mutex, kfifo, videodev2, ratelimit, V4L2 controls/device/fh, vb2-v4l2, and `coda_regs.h`. Risks are broad blast radius from structure changes, mixed lock ownership across context fields, shared encoder/decoder use of `coda_params`, and the duplicated inline/prototype shape of `coda_bitstream_can_fetch_past()`. Test by building all CODA objects, opening each video node, streaming encode/decode/JPEG paths, and validating controls/events/metadata under lockdep.
