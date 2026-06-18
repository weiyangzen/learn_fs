# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/acornfb.h

Purpose: RiscPC framebuffer platform definitions for Acorn video modes, memory, and monitor configuration.

Important APIs/types/functions: declares/defines Acorn framebuffer data structures and constants used by the Acorn framebuffer driver and machine setup to describe VRAM, default modes, sync/timing, and monitor type.

Control flow: no executable flow; it is a platform ABI header for framebuffer setup.

State and persistence: structures describe boot-time framebuffer configuration and video memory layout.

Dependencies and integration points: consumed by RiscPC machine code and the `acornfb` driver.

Risks: stale mode/timing values can produce unusable display output. Header is platform-specific and not DT-discoverable.

Test signals: framebuffer probe, correct video mode selection, VRAM mapping, and console output on RiscPC displays.
