# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-debugfs.c

## Purpose
`visl-debugfs.c` implements optional debugfs dumping of submitted OUTPUT bitstream buffers. It gives stateless decoder developers a way to inspect raw encoded payloads for selected frame ranges, similar in spirit to userspace media API trace buffers.

## Important APIs, types, and functions
`visl_debugfs_init()` creates `/sys/kernel/debug/visl`, initializes `dev->bitstream_blobs`, initializes `dev->bitstream_lock`, and calls `visl_debugfs_bitstream_init()` to create the `bitstream` directory. `visl_trace_bitstream()` copies the current source buffer payload from `vb2_plane_vaddr()` into a `vzalloc()`-backed `debugfs_blob_wrapper`, creates a read-only `bitstream%d` file keyed by the OUTPUT sequence, and appends the wrapper to `dev->bitstream_blobs`. `visl_debugfs_clear_bitstream()` removes all tracked blobs under `bitstream_lock`. `visl_debugfs_bitstream_deinit()` and `visl_debugfs_deinit()` clear blobs and remove directories recursively.

## Control flow
The core probe calls `visl_debugfs_init()`. During `visl_device_run()`, the decoder calls `visl_trace_bitstream()` only if the current destination sequence is inside the configured `bitstream_trace_frame_start`/`bitstream_trace_nframes` window. Stream stop calls `visl_debugfs_clear_bitstream()` unless `keep_bitstream_buffers` is set. Device release always deinitializes debugfs.

## State and persistence
The persistent state is the `struct visl_blob` list held by `struct visl_dev`. Each blob owns a copied payload buffer and a debugfs dentry. Blobs may survive streamoff if `keep_bitstream_buffers` is true, but module/device teardown removes them unconditionally.

## Dependencies and integration points
The file depends on debugfs, vb2 payload access, V4L2 mem2mem buffer structures, `struct visl_run`, and the `CONFIG_VISL_DEBUGFS` members in `struct visl_dev`. It is called from core probe/release and decode/streamoff paths.

## Risks and test signals
The main risks are memory growth when large payloads are preserved, silent loss of trace data when allocations or debugfs creation fail, and reliance on a valid plane virtual address. Test signals include blob creation with expected byte contents for traced frames, cleanup on streamoff, persistence when `keep_bitstream_buffers=1`, and absence of leaks under repeated tracing.
