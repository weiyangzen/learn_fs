# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_dmm_tiler.h

Purpose: Declares the public OMAP DMM/TILER API, tiler formats, block/area structures, orientation/address constants, sizing helpers, and platform driver symbol.

Important APIs/types: `enum tiler_fmt` defines 8-bit, 16-bit, 32-bit, and page modes. `struct pat_area` encodes hardware PAT rectangle coordinates. `struct tiler_block` stores allocation list node, TCM area, and format. Constants define slot/container geometry, TILER view base addresses, orientation bits, access-mode shift, and `TIL_ADDR()`. APIs reserve/release blocks, pin/unpin pages, produce system-space and transformed-space pointers, calculate stride/size/virtual size, align dimensions, return CPU cache flags, and report DMM availability. `gem2fmt()` maps OMAP GEM tiling flags to TILER formats.

Control flow: GEM and framebuffer code reserve blocks for tiled buffers, pin pages before scanout, compute rotated addresses for DISPC, and release blocks when BOs go away. fbdev uses page-mode rolling through GEM/TILER integration.

State and persistence: Public `tiler_block` objects represent live TILER allocations until release. Header itself stores no state.

Dependencies/integration: Includes `omap_drv.h` for OMAP BO flags and `tcm.h` for container allocator types. Integrates with GEM, framebuffer scanout, fbdev, debugfs, and the DMM platform driver.

Risks and test signals: Geometry constants and orientation bit definitions must match hardware TRM. `validfmt()` and `gem2fmt()` are relied on before BUG_ON paths. Test all tiler formats, rotations/reflections, NV12/YUYV address calculations, page-mode ywrap, and builds with/without debugfs.
