# sources/distributed-fs/ceph-client/include/video/newport.h

## Purpose
`newport.h` defines the SGI NEWPORT graphics hardware register layout, draw-mode/control bitfields, context snapshot type, and inline helper routines for VC2, color map, XMAP9, and busy-wait operations.

## Important APIs, Types, and Functions
Core MMIO types are `npireg_t`, `npfreg_t`, `union np_dcb`, `struct newport_rexregs`, `struct newport_cregs`, `struct newport_regs`, and `newport_ctx`. Register fields cover REX draw modes, plane/depth/source/blend/logical-op bits, geometry iterators, color/slope values, DCB mode/data, configuration/status bits, VC2 indexed registers/control bits, color-map access, DCB protocol cycles, XMAP9 FIFO/mode controls, and BT445 access. Inline helpers include `newport_vc2_set()`, `newport_vc2_get()`, `newport_cmap_setaddr()`, `newport_cmap_setrgb()`, `newport_wait()`, `newport_bfwait()`, `xmap9FIFOWait()`, and `xmap9SetModeReg()`.

## Control Flow
Drivers write `regs->set` to stage REX/DCB state and `regs->go` to execute operations. VC2 helpers write DCB mode words, send indexed register addresses and data, and read back indexed values. Color-map helpers set an address and stream RGB data. Busy waits poll graphics or bus-busy status until idle or timeout. XMAP9 programming waits for FIFO availability and selects protocol timing based on clock frequency.

## State and Persistence Behavior
Hardware state includes REX draw registers, clipping/configuration, DCB devices, VC2 timing/cursor/display controls, color maps, and XMAP9 mode registers. `newport_ctx` can snapshot selected graphics state for context save/restore. No file-backed persistence exists.

## Dependencies and Integration Points
It integrates SGI framebuffer/graphics code with NEWPORT REX, VC2 video timing, CMAP/XMAP RAMDAC-style devices, and DCB bus protocols. It uses volatile MMIO structure access rather than accessor functions.

## Risks and Test Signals
Risks include endian-sensitive DCB byte/word access, busy-wait timeout tuning, incorrect set/go register selection, DCB protocol timing mistakes at different pixel clocks, and context save omissions. Test signals include mode setup through VC2, palette updates, XMAP9 mode programming at multiple clock ranges, accelerated draw operations, timeout-path tests for busy waits, and visual cursor/color correctness.
