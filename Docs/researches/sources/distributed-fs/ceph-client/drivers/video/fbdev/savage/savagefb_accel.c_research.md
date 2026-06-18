# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb_accel.c

Purpose: optional hardware acceleration implementation for Savage fbdev. It emits BCI 2D commands for synchronization, rectangle copy, solid fill, and 1 bpp monochrome image blits.

Important APIs/types/functions: exported fbdev callbacks are `savagefb_sync`, `savagefb_copyarea`, `savagefb_fillrect`, and `savagefb_imageblit`. `savagefb_rop` maps fbdev ROP_COPY/ROP_XOR to hardware ROP codes. The code relies on `BCI_SEND`, `BCI_CMD_*`, `BCI_X_Y`, `BCI_W_H`, `BCI_CLIP_LR`, and the chipset-specific `SavageWaitIdle`/`SavageWaitFifo` callbacks initialized by the main driver.

Control flow: each operation exits early for zero-sized work. Copy computes direction bits and adjusts source/destination corners for overlap-safe copies, waits for four FIFO slots, and sends source, destination, and size. Fill resolves the color through pseudo_palette for truecolor modes, sets ROP and solid-source command bits, waits for FIFO space, and sends color/location/size. Imageblit falls back to `cfb_imageblit` unless depth is 1, computes foreground/background colors, rounds width to 32 pixels, waits for all command/data words, and streams the bitmap data.

State and persistence: no independent state is allocated. Operations mutate hardware command FIFO and `par->bci_ptr`; persistent acceleration parameters such as depth, virtual width, BCI base, and wait callbacks live in `struct savagefb_par`.

Dependencies and integration: built only with `CONFIG_FB_SAVAGE_ACCEL` and selected by `savagefb_ops` in the main driver. Requires the main driver's `SavageSetup2DEngine` to have configured BCI, global bitmap descriptor, clipping, and wait functions.

Risks: FIFO wait requests are based on calculated command sizes; incorrect size can overflow the BCI FIFO. `rect->rop` indexes `savagefb_rop` without local bounds checking, relying on fbdev callers to pass valid ROP values. `image->data` is cast to `u32 *`, so alignment and padding assumptions matter. Busy-waiting on broken hardware can stall the caller.

Test signals: accelerated console scroll/copy, fillrect with COPY and XOR, truecolor and pseudocolor fills, monochrome font/image blits with non-32-pixel widths, fallback for non-1bpp image data, and `fb_sync` waiting for idle after command submission.
