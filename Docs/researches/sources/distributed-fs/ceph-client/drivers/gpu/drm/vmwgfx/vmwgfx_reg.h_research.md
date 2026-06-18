# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_reg.h

Purpose: Minimal kernel-space SVGA virtual hardware register include wrapper. It defines a few vmwgfx-side structures/constants and includes the main SVGA3D register definitions.

Important APIs/types/functions: `struct svga_guest_mem_descriptor` holds a physical page number and page count. `struct svga_fifo_cmd_fence` holds a FIFO fence value. `SVGA_SYNC_GENERIC` and `SVGA_SYNC_FIFOFULL` define sync reason constants. The header then includes `device_include/svga3d_reg.h`, which supplies the command/register structures used throughout vmwgfx.

Control flow: None at runtime; this file is compile-time type and constant plumbing.

State and persistence: None. Hardware state is managed by callers using the included register definitions.

Dependencies and integration points: Included by driver code needing SVGA3D command layouts and register constants. Risks are low but include ABI drift between local wrapper structs and device headers, and broad compile breakage if included headers change. Test signals: build coverage across files using SVGA commands, fence command encoding, and register write paths.
