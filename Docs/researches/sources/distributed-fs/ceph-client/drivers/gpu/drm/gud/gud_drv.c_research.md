
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_drv.c

## Purpose
`gud_drv.c` is the Generic USB Display driver core. It owns USB probe/disconnect/power-management, protocol control transfers, display descriptor validation, DRM device and mode-config setup, format discovery and XRGB8888 emulation selection, bulk buffer allocation, plane/CRTC registration, connector discovery, debugfs statistics, and module registration.

## Important APIs, Types, And Functions
Internal DRM formats `gud_drm_format_r1` and `gud_drm_format_xrgb1111` describe protocol-only transfer formats. Exported internal USB helpers are `gud_usb_get()`, `gud_usb_set()`, `gud_usb_get_u8()`, and `gud_usb_set_u8()`. Major helpers include `gud_usb_control_msg()`, `gud_get_display_descriptor()`, `gud_status_to_errno()`, `gud_usb_get_status()`, `gud_usb_transfer()`, `gud_plane_add_properties()`, `gud_stats_debugfs()`, `gud_alloc_bulk_buffer()`, `gud_free_buffers_and_mutex()`, `gud_probe()`, `gud_disconnect()`, `gud_suspend()`, and `gud_resume()`.

The file defines the DRM callback tables for CRTC, plane, mode config, GEM fops, and `struct drm_driver`, and registers a USB driver with two vendor-specific USB IDs.

## Control Flow
Probe finds a bulk-out endpoint, reads and validates the GUD display descriptor, rejects unsupported protocol versions and inconsistent dimensions, allocates a managed `struct gud_device`, records flags/compression, initializes locks and flush work, sets USB interface data, optionally attaches the USB DMA device, initializes DRM mode config bounds, and discovers protocol formats through `GUD_REQ_GET_FORMATS`.

Supported protocol pixel formats are converted to DRM fourcc values. Internal R1 and XRGB1111 formats are kept for transfer conversion but not exposed to userspace. If the gadget lacks XRGB8888 but supports an emulatable lower-depth format, the driver exposes XRGB8888 to userspace and stores the emulation format for `gud_pipe.c`. It caps max bulk buffer size at 64 MiB, allocates a vmalloc buffer and scatterlist, allocates LZ4 memory if advertised, initializes a primary plane with damage clips, adds plane properties, creates one CRTC, discovers connectors, resets mode config, starts polling, adds debugfs stats, registers the DRM device, and starts DRM client setup.

USB control transfers are serialized by `ctrl_lock` and guarded by `drm_dev_enter()`. On control stalls or `STATUS_ON_SET` devices, `gud_usb_transfer()` reads `GUD_REQ_GET_STATUS` and maps protocol status codes to Linux errno values. Disconnect stops polling, unplugs the DRM device, and shuts down atomic state. Suspend and resume use DRM mode-config helper suspend/resume.

## State And Persistence
`struct gud_device` holds device flags, supported properties, bulk pipe and buffer metadata, compression buffers, transfer statistics, control and damage locks, and framebuffer damage state. Probe-created DRM objects persist until USB disconnect or device-managed cleanup. Debugfs reports max buffer size, error count, compression modes, and compression ratio derived from accumulated stats.

## Dependencies And Integration Points
The file depends on the USB core, DRM KMS/GEM shmem/fbdev/client helpers, LZ4, scatter-gather APIs, `<drm/gud.h>` protocol definitions, `gud_internal.h`, `gud_pipe.c` plane/CRTC helpers, and `gud_connector.c` connector discovery. Kconfig selects the needed helper libraries.

## Risks
The driver trusts the gadget enough to allocate buffers based on advertised dimensions and formats, mitigated by a 64 MiB cap. `GUD_DISPLAY_FLAG_FULL_UPDATE` is rejected with compression because the pipe path's full-update behavior conflicts with compressed rectangle metadata. `gud_usb_get_u8()` writes `*val` before checking transfer status, so callers must honor the return value. Misreported format lists can leave no exposed formats or force expensive emulation. Control transfers are synchronous and can block up to USB timeouts.

## Test Signals
Test probe with valid and malformed descriptors, unsupported protocol versions, missing bulk endpoints, empty/unknown format lists, XRGB8888 emulation paths, LZ4 and no-compression devices, plane rotation property discovery, connector discovery failure paths, debugfs stats after flushes, USB stall/status mapping, disconnect during active flush, and suspend/resume with active modes.
