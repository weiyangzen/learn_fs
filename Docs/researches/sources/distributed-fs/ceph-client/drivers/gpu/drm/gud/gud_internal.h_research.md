
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_internal.h

## Purpose
`gud_internal.h` defines the internal state and helper API shared by the Generic USB Display implementation files.

## Important APIs, Types, And Functions
The central type is `struct gud_device`, which embeds the DRM device, primary plane, CRTC, flush work, protocol flags, XRGB8888 emulation format, device property list, USB bulk transfer state, compression buffers, transfer statistics, control lock, damage lock, pending framebuffer/damage state, and optional shadow buffer.

It declares internal USB helpers, flush and atomic helpers, connector helpers, and the custom internal formats `GUD_DRM_FORMAT_R1` and `GUD_DRM_FORMAT_XRGB1111`. Inline helpers include `to_gud_device()`, `gud_to_usb_device()`, `gud_from_fourcc()`, `gud_to_fourcc()`, `gud_from_display_mode()`, and `gud_to_display_mode()`.

## Control Flow
The header has no standalone runtime flow, but its conversion helpers are in the active paths. Probe maps gadget pixel format IDs to DRM fourcc values with `gud_to_fourcc()`. Atomic state check maps the selected transfer format back with `gud_from_fourcc()`. Connector mode enumeration and atomic state serialization convert between DRM mode structures and little-endian GUD protocol mode structures.

## State And Persistence
All persistent driver-private state is described by `struct gud_device`. Control transfers are serialized by `ctrl_lock`; damage accumulation and async flushing are protected by `damage_lock`; `fb`, `damage`, `prev_flush_failed`, and `shadow_buf` persist between atomic updates and queued flush work.

## Dependencies And Integration Points
It depends on Linux list/mutex/scatterlist/USB/workqueue headers, DRM mode types, UAPI fourcc values, and protocol definitions from `<drm/gud.h>` included by the implementation files. It is the contract between `gud_drv.c`, `gud_pipe.c`, and `gud_connector.c`.

## Risks
Format conversion returns zero for unknown formats, so callers must reject zero before using it in protocol state. Mode conversion masks user-visible mode flags to `GUD_DISPLAY_MODE_FLAG_USER_MASK`, so unsupported future flags are intentionally dropped. The internal custom fourcc values must remain private and must not be exposed to userspace.

## Test Signals
Compile-time coverage across all three GUD C files is required. Runtime signals include correct protocol format mapping, correct preferred-mode flag round-trips, accurate connector property serialization, and absence of races between control transfers and asynchronous damage flushing.
