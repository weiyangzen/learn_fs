# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vboxvideo_guest.h

## Purpose

`vboxvideo_guest.h` declares the guest-side helper API for VirtualBox HGSMI/VBVA operations and defines the per-screen VBVA buffer context.

## Important APIs, Types, and Functions

- `struct vbva_buf_ctx`: stores buffer VRAM offset/length, overflow flag, active record pointer, and mapped `vbva_buffer` pointer.
- HGSMI helper prototypes for flags location, capabilities, config queries, cursor shape, display info, input mapping, and mode hints.
- VBVA ring helper prototypes for enable/disable, begin/end update, write, and context setup.

## Control Flow

Mode, IRQ, and hardware setup code call these helpers without needing the low-level buffer header details. `vbva_buffer_begin_update`, `vbva_write`, and `vbva_buffer_end_update` form the record-writing sequence for dirty rectangles.

## State and Persistence Behavior

`vbva_buf_ctx` persists per CRTC while acceleration is enabled. It tracks whether a ring buffer is mapped/enabled, whether an update is active, and whether overflow occurred.

## Dependencies and Integration Points

The header includes Linux genalloc and `vboxvideo.h`, and is included by `vbox_drv.h` and most protocol implementation files. It is the internal API surface between KMS code and transport code.

## Risks and Edge Cases

Callers must pair begin/end update and must not write when `record` is null or overflowed. Buffer offsets and lengths must match host-visible VRAM layout established during hardware init.

## Test Signals

Build checks for prototypes, VBVA begin/write/end sequencing tests, buffer overflow handling, and integration tests from plane damage updates to host flushes.
