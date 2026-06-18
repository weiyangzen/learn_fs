<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vt.h

Purpose: defines Linux virtual terminal ioctl numbers and structures for VT switching, process-controlled release/acquire, resizing, event wait, and console state queries.

Important APIs and types: constants cover console count bounds and ioctls from `VT_OPENQRY` through `VT_GETCONSIZECSRPOS`. `struct vt_mode` configures automatic or process-controlled switching and signals. `struct vt_stat`, `vt_sizes`, `vt_consize`, `vt_event`, `vt_setactivate`, and `vt_consizecsrpos` define state, geometry, event, activation, and cursor-size payloads.

Control flow, state, and persistence: userspace queries/sets VT mode, activates or waits for consoles, acknowledges release/acquire, resizes kernel console geometry, and waits for switch/blank/unblank/resize events. VT state persists while consoles exist.

Dependencies and integration points: integrates with tty/vt console code, framebuffer/DRM console layers, session managers, and terminal emulators.

Risks and test signals: risks include signal races, historical `VT_GETSTATE` short limits, resize geometry mismatch, and event bitmask validation. Test process-controlled switching, lock/unlock switch, resize ioctls, event waits, and cursor position queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vt.h -->
