# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_instance.h

## Purpose
`iris_instance.h` defines the per-open video session state shared across decoder, encoder, HFI, controls, buffers, power, and V4L2 queue code.

## Important APIs, Types, And Functions
It defines default dimensions, output codec format type enum, capture raw format type enum, `struct iris_fmt`, and `struct iris_inst`. The instance holds list linkage to the core, session id, queue and forward/reverse locks, V4L2 file handle, source/destination formats, control handler, domain, crop/compose rectangles, completions, flush response count, firmware caps, buffer arrays, firmware min count, instance state/sub-state, once-per-session flag, max input data size, power and interconnect votes, mem2mem device/context, output/capture sequence counters, timestamp metadata ring, codec, last-buffer flag, frame/operating rates, HFI rate-control type, and encoder raw/scaled dimensions.

## Control Flow
Instances are allocated by generation-specific allocators, initialized by decoder or encoder code, attached to `core->instances`, and then passed through all V4L2 operations. HFI commands use `session_id`, formats, crop/compose, caps, buffers, state, and completions. HFI responses find instances by session id and mutate buffer/state/format fields under `inst->lock`.

## State And Persistence Behavior
The structure persists for one file/session lifetime. It is the main persistence boundary for stream configuration, controls, queue state, firmware/session state, and power votes. The timestamp metadata ring bridges output timestamps/timecode into capture completions.

## Dependencies And Integration Points
It includes V4L2 controls, `iris_buffer`, `iris_core`, and utility types. It is consumed by nearly every Iris source file. Gen2 embeds this struct in a larger wrapper; Gen1 allocates it directly.

## Risks And Test Signals
Locking is split between `ctx_q_lock` for queue ioctls and `lock` for forward/reverse thread serialization; races should be tested around qbuf/streamoff/IRQ completion. Since many fields are updated by both userspace ioctl paths and firmware response paths, tests should stress concurrent streamoff, DRC, drain, close, and system-error handling.
