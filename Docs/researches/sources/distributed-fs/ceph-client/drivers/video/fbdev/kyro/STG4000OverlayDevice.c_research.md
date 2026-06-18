
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000OverlayDevice.c

Purpose: programs STG4000 video overlay surfaces, scaling/decimation, blending, viewport, and overlay enable registers for the Kyro framebuffer driver's private overlay ioctls.

Important APIs and data: `ResetOverlayRegisters()` disables/clears overlay address, size, decimation, pixel format, scaling, and blend mode. `CreateOverlaySurface()` validates dimensions, calculates linear or planar strides, writes Y/U/V addresses, stores static overlay dimensions/stride/format, and returns byte strides. `SetOverlayBlendMode()` programs graphics, color key, alpha, and combined modes. `SetOverlayViewPort()` calculates source/destination clipping, vertical decimation, horizontal decimation/scaling, line-store stride, overlay size, window start/end, pixel-format excess pixels, and scaler registers. `EnableOverlayPlane()` turns on overlay stream bits.

Control flow: `fbdev.c` first calls `ResetOverlayRegisters()` during each video mode set. Overlay create ioctl calls `CreateOverlaySurface()` once per mode and then default global alpha blend. Viewport ioctl disables RAMDAC output, calls `SetOverlayViewPort()`, enables overlay plane, and re-enables output.

State and persistence: file-static `ovlWidth`, `ovlHeight`, `ovlStride`, and `ovlLinear` persist the last created overlay and are required by viewport programming. Device-wide offsets and returned strides are kept in `fbdev.c`'s `deviceInfo`.

Dependencies and integration: uses `STG4000Reg.h` read/write/bit macros and overlay blend enums. It assumes framebuffer memory layout is managed by the caller and that overlay offsets are already aligned sufficiently.

Risks: static overlay state makes the implementation effectively single-device/single-overlay. Planar UV size expression `(inWidth + 1 / 2)` is suspicious because integer precedence makes `1 / 2` zero. Scaling math has many divisions and boundary cases; some invalid viewport cases are rejected by caller, but not all. Hardware comments note uncertain blend semantics.

Test signals: valid/invalid overlay dimensions, linear and planar stride/UV offset calculations, one-overlay-only behavior, viewport zero/underflow rejection, downscale/upscale cases, alpha/color-key modes, and visual verification of YUV alignment and clipping.
