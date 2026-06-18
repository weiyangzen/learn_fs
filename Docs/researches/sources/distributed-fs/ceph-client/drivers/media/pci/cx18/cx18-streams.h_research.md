# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-streams.h

Exposes cx18 stream lifecycle, firmware queue submission, stream enabled checks, and handle lookup helpers. Key APIs are `cx18_streams_setup`, `cx18_streams_register`, `cx18_streams_cleanup`, `cx18_stream_enabled`, `cx18_stream_put_mdl_fw`, `cx18_start_v4l2_encode_stream`, and `cx18_stop_v4l2_encode_stream`.

The inline firmware submission path enqueues an MDL to `q_free` and schedules work to submit it to firmware asynchronously. `cx18_stream_enabled` normalizes V4L2, DVB, and IDX enablement checks.

State is mutated in stream objects and firmware queues. Risks are callers assuming synchronous submission, disabled stream confusion, and stale handles after task destruction. Test signals are queue refill behavior, handle lookup, and disabled stream short-circuiting.
