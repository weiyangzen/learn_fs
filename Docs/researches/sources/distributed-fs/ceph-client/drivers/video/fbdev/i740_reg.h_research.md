<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i740_reg.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/i740_reg.h

Purpose: defines Intel740 VGA, extended VGA, multimedia, FIFO, interrupt, and BitBLT register offsets and bit masks used by `i740fb.c`.

Important APIs, types, and functions: there are no functions or types. Constants cover DAC ports, CRTC extension registers, misc output, system configuration extension registers such as `ADDRESS_MAPPING`, DRAM detection/control, DPMS, pixel-pipe configuration, cursor registers, VCLK2 PLL registers, multimedia overlay controls, FIFO status, interrupt masks, FIFO watermark/burst control, and BitBLT command registers/fields.

Control flow: this header shapes the implementation's control flow by naming the registers that `i740fb_decode_var()`, `i740fb_set_par()`, DDC bit-banging, blanking, memory detection, and optional BLT setup write.

State and persistence: all definitions refer to hardware state. The persistent software copy of these fields lives in `struct i740fb_par` in `i740fb.c`.

Dependencies and integration points: included by `i740fb.c`; many definitions are paired with VGA port helpers from `<video/vga.h>`. The BitBLT and FIFO definitions are present even though this driver marks acceleration as none and mainly uses mode programming/DPMS/DDC paths.

Risks: incorrect constants can corrupt VGA register programming. Many registers are legacy VGA indexed ports, where write order and protection bits matter. Some fields such as 32 bpp dynamic depth are explicitly noted as unimplemented on i740.

Test signals: compile coverage through `i740fb.c`, register trace comparison during set_par/blank/DDC, and static checks that fields used in masks match intended register widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/i740_reg.h -->
