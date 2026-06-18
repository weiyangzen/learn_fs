<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbus428ctldefs.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usbus428ctldefs.h

## Purpose
Defines US-428 control-surface data structures shared between the kernel driver and userspace via hwdep mmap.

## APIs, Types, and Functions
Defines control indices (`enum E_IN84`), transport button masks, `struct us428_ctls`, output update structures `us428_set_byte`, `usx2y_volume`, `us428_lights`, `us428_p4out`, buffer counts, and `struct us428ctls_sharedmem`. `US428_SHAREDMEM_PAGES` is the page-aligned mmap allocation size.

## Control Flow, State, and Persistence
No executable flow. Persistent shared state records a ring of control snapshots, the byte offset that differed, reader/writer cursors, a ring of pending pipe-4 output commands, and output sent/last cursors. The interrupt pipe-4 handler in `usbusx2y.c` writes snapshots and drains light/volume output requests.

## Dependencies and Integration
Used by `usX2Yhwdep.c` for mmap/poll sizing and by `usbusx2y.c` for interrupt-pipe control updates. It depends on `PAGE_ALIGN` from kernel headers via including source context.

## Risks and Test Signals
Risks include packed layout assumptions without explicit packing, signed cursor sentinel values in shared memory, loss of output commands when multiple p4out entries arrive, and userspace ABI rigidity. Test signals are US-428 fader/button updates, light/volume writes, wraparound of both rings, and mmap size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usbus428ctldefs.h -->
