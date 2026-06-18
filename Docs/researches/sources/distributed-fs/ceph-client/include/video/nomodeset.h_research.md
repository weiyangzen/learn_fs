# sources/distributed-fs/ceph-client/include/video/nomodeset.h

## Purpose
`nomodeset.h` declares the shared helper that tells display drivers whether boot policy restricts them to firmware-provided display drivers only.

## Important APIs, Types, and Functions
The only API is `bool video_firmware_drivers_only(void);`.

## Control Flow
Display drivers call the helper during probe or modeset-driver selection. A true result should make native modesetting drivers defer or avoid binding so firmware framebuffer/simple display drivers remain in control.

## State and Persistence Behavior
The header owns no state. The implementation likely reflects boot parameters or global video policy established during kernel initialization; that policy persists for the boot session.

## Dependencies and Integration Points
It integrates DRM/fbdev/native graphics drivers with global video boot policy and firmware framebuffer fallback behavior.

## Risks and Test Signals
Risks include drivers ignoring the helper, using it too late after hardware takeover, or returning inconsistent policy between built-in and module drivers. Test signals include booting with and without `nomodeset`, verifying native GPU driver probe suppression, firmware framebuffer retention, and no regression for drivers that are themselves firmware/simple display drivers.
