<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.c

## Purpose
`xe_eu_stall.c` implements EU stall observation streams. It lets privileged userspace open an anonymous fd, enable hardware sampling, poll/read per-XeCore stall records, and disable/close the stream.

## Important APIs, types, and functions
Data structures include per-XeCore circular-buffer pointers, `xe_eu_stall_data_stream`, GT-level `xe_eu_stall_gt`, open properties, and packed PVC/Xe2/Xe3p record formats. Public helpers report supported sampling rates, per-XeCore buffer size, record size, initialize GT state, and open a stream. Internal paths parse user extensions, allocate GGTT-mapped system BO buffers, program MCR EU stall registers, poll write pointers, copy records to userspace, report drop bits, and handle enable/disable ioctls.

## Control flow and integration points
`xe_eu_stall_stream_open()` validates platform support and perf permissions, parses properties, requires a GT id, serializes on `stream_lock`, allocates one stream, initializes buffers, and returns an anon inode fd. Enable takes runtime PM and render forcewake, applies WA `22016596838` if needed, initializes read/write pointers, programs MOCS/sample rate/base registers, and starts delayed polling. Polling checks all DSS steering instances every 5 ms and wakes readers once enough rows are present. Read aligns user count to record size, blocks unless `O_NONBLOCK`, copies circular data across wrap boundaries, advances hardware read pointers, and reports drops as `-EIO` once.

## State and persistence behavior
One stream can exist per GT. The stream owns a pinned GGTT BO, per-XeCore buffer metadata, waitqueue, delayed work, forcewake ref, runtime PM ref while enabled, and data-drop bitmap. Close disables sampling, frees the BO, clears `gt->eu_stall->stream`, and drops the DRM device ref.

## Dependencies, risks, and test signals
Dependencies include observation ioctls, anon inodes, MCR register access, forcewake, runtime PM, GT topology, GGTT BO allocation, MOCS, platform workarounds, and generated WA identifiers. Risks include pointer wrap math, buffer overflow/drop reporting, single-stream locking, enable failure leaving `enabled` true, small read buffer behavior, forcewake leaks, and unsupported platform exposure. Test signals include open/enable/poll/read/disable/close, blocking and nonblocking reads, drop-bit injection, PVC/Xe2/Xe3p record-size checks, GT id validation, perf permission checks, runtime PM, and suspend/removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_eu_stall.c -->
