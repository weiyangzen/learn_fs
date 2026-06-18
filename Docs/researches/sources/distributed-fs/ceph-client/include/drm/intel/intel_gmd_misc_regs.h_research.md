# sources/distributed-fs/ceph-client/include/drm/intel/intel_gmd_misc_regs.h

Purpose: defines miscellaneous Intel graphics/display MMIO registers used for display arbitration, FBC behavior, tiling swizzle, and instruction/power-management control.

Important APIs/types/functions: `DISP_ARB_CTL` carries `DISP_FBC_MEMORY_WAKE`, `DISP_TILE_SURFACE_SWIZZLING`, and `DISP_FBC_WM_DIS`. `INSTPM` carries legacy self-enable, AGPBUSY interrupt enable, force ordering, TLB invalidate, and sync flush bits.

Control flow: display and GT init paths read/modify/write these registers to configure memory arbitration, FBC behavior, tiling surface interpretation, ordering, and flush/invalidate operations.

State and persistence: the state is hardware register state that may be reprogrammed at init and resume. No software state is declared.

Dependencies and integration: expects `_MMIO`, `REG_BIT`, and Intel register access helpers. Integrated by display watermark/FBC and GT flush paths.

Risks and test signals: wrong bit use can break framebuffer compression, tiling, interrupt delivery from low power states, or TLB coherency. Test FBC enable/disable, tiled framebuffer scanout, suspend/resume, and forced flush/invalidate paths.
