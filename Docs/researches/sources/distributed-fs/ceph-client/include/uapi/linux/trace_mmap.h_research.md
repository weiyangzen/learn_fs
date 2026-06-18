# sources/distributed-fs/ceph-client/include/uapi/linux/trace_mmap.h

Purpose: Defines metadata shared with userspace for mmap-backed tracing buffers.

Important APIs/types/functions: `struct trace_buffer_meta` exposes buffer metadata including event sub-buffer size/count, reader identity, flags, entries, overrun count, read counters, and reserved fields for future expansion. `TRACE_MMAP_IOCTL_GET_READER` retrieves reader state.

Control flow: A tracing consumer maps a trace buffer and reads metadata to coordinate sub-buffer consumption. The ioctl provides an explicit reader pointer/index update path for consumers that cannot infer it from mapped metadata alone.

State and persistence behavior: Metadata is live shared state maintained by tracing infrastructure. It is volatile and tied to the tracing instance and mapping lifetime.

Dependencies and integration points: Depends on `linux/types.h`, tracing ring-buffer internals, and ioctl plumbing. Consumers include tracing tools that avoid copy-heavy reads.

Risks: Shared-memory ABI must handle producer/consumer races, alignment, and reserved-field zeroing. Readers need memory-ordering discipline around counters and buffer indices.

Test signals: mmap tracing buffers, verify metadata updates under high event rates, ioctl reader retrieval, overrun accounting, sub-buffer wraparound, and 32/64-bit layout stability.
