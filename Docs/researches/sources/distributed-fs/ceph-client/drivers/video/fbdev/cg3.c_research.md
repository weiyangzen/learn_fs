# sources/distributed-fs/ceph-client/drivers/video/fbdev/cg3.c

## Purpose
`cg3.c` is the Open Firmware/platform fbdev driver for Sun CGthree color framebuffers and cgRDI variants. It maps 8-bit framebuffer memory, manages the Brooktree-style DAC colormap, programs default timing tables when firmware lacks dimensions, and implements blanking plus SBUS compatibility mmap/ioctl paths.

## Important APIs, Types, and Functions
Key types are `struct cg3_regs`, `struct bt_regs`, `enum cg3_type`, and `struct cg3_par`. fbdev operations are `cg3_setcolreg()`, `cg3_blank()`, `cg3_sbusfb_mmap()`, and `cg3_sbusfb_ioctl()`. Initialization helpers include `cg3_rdi_maybe_fixup_var()`, `cg3_do_default_mode()`, and `cg3_init_fix()`.

## Control Flow
`cg3_probe()` allocates fb state, fills var from OF, detects cgRDI and optional `params`, computes linebytes and smem length, maps registers and RAM, unblanks, optionally programs default timing/DAC values, allocates and installs a 256-entry colormap, initializes fix info, registers the framebuffer, and stores driver data. Remove unregisters, frees cmap, unmaps, and releases fb state.

## State and Persistence
`struct cg3_par` stores a lock, register mapping, software colormap shadow, flags, and IO-space ID. Hardware state includes control video enable, timing registers, DAC control, DAC color map, and framebuffer contents. The software colormap shadow exists because hardware palette loads are grouped in an unusual 4-entry/3-word pattern.

## Dependencies and Integration Points
The driver depends on OF resources, SBUS helpers/accessors, `sbuslib.h`, Sun fbio type `FBTYPE_SUN3COLOR`, and fbdev colormap installation. It binds both `cgthree` and `cgRDI`.

## Risks and Edge Cases
Palette writes are nontrivial and depend on the shadow buffer staying coherent. Unknown status register IDs fail timing setup. cgRDI parameter parsing is permissive and only recognizes `WxH-` prefixes. The driver assumes fixed register/RAM offsets within resource 0.

## Test Signals
Signals include visible 8-bit pseudocolor output, correct colormap changes for arbitrary indices, blank/unblank toggling video, cgRDI resolution override from OF params, 66Hz/76Hz/RDI timing table selection, SBUS mmap at `CG3_MMAP_OFFSET`, and correct fbio type/size reporting.
