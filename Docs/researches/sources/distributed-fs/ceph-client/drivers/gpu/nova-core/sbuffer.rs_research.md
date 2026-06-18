# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/sbuffer.rs

Purpose: stream-like abstraction over multiple discontiguous byte slices for reading from and writing into scatter buffers.

Important APIs and types: `SBufferIter<I>` stores a current non-empty slice plus remaining slices. `new_reader()` and `new_writer()` construct reader/writer views. Reader methods include `read_exact()`, `flush_into_kvec()`, and `Iterator<Item = u8>`. Writer method `write_all()` copies a source byte stream across mutable slices.

Control flow: construction skips empty slices. `get_slice_internal()` returns either a whole current slice or splits it, advancing to the next non-empty slice as needed. Reader/writer loops repeat until the requested data is consumed or return `EINVAL`/`ETOOSMALL`.

State and persistence: state is only iterator position and the current slice remainder. It mutates destination slices for writers and consumes reader position.

Dependencies and integration: depends on kernel allocation flags and `KVec`. Used by GSP command/message code, including sequencer message collection from split command buffers.

Risks: lifetime correctness depends on typed reader/writer constructors. `flush_into_kvec()` allocates and can fail. Iterator byte-by-byte reading is simple but may be inefficient for large buffers.

Test signals: documented examples cover split writes and byte summing. Integration signals include GSP command serialization/deserialization across multiple queue buffers.
