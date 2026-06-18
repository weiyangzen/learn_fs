# sources/distributed-fs/ceph-client/drivers/video/fbdev/pxa3xx-regs.h

Purpose: supplies PXA2xx/PXA3xx LCD controller register offsets and bitfield macros used by `pxafb.c` for base plane, overlays, palette DMA, interrupts, timing, and smart-panel command programming.

Important APIs/types/functions: no functions or structs are defined. Major register offsets include `LCCR0` through `LCCR5`, `LCSR`/`LCSR1`, branch registers `FBR0` through `FBR6`, overlay controls `OVL1C*`/`OVL2C*`, command/status registers `CMDCR` and `PRSR`, frame descriptor registers `FDADR0` through `FDADR6`, and TMED registers. Macros encode control bits such as `LCCR0_ENB`, `LCCR0_LCDT`, `LCCR0_OUC`, `LCCR3_BPP`, `LCCR3_PixClkDiv`, `LCCR4_PAL_FOR_*`, interrupt masks/status bits, `LDCMD_PAL`, overlay dimensions/position/format, and smart-panel status flags.

Control flow: `pxafb.c` uses this header to derive shadow register values in mode activation, program panel timing, enable/disable the LCD controller, construct DMA descriptors with palette chaining, branch to new frame descriptors for panning and overlays, handle disable/command/branch interrupts, and encode overlay dimensions and pixel formats.

State and persistence: the header defines MMIO state layout only. Actual state persists in LCD controller registers and DMA descriptor memory managed by `pxafb.c`. Macros such as `LCCR1_DisWdth`, `LCCR2_DisHght`, and `OVLxC1_PPL` encode "value minus one" hardware fields, so caller inputs become persistent hardware timing.

Dependencies and integration: local to the fbdev PXA driver family in this source set. It is included by `pxafb.c`, which supplies register accessors and policy. It reflects hardware definitions and must remain aligned with platform data flags from `<linux/platform_data/video-pxafb.h>`.

Risks: macro arguments are not range checked and can underflow for zero values in "minus one" encoders. Some branch register comments are copy-pasted and label several registers as DMA channel 2. Polarity macros use multiplication by zero/one constants, which can be surprising but is intentional for bit selection. Incorrect mask use can leave interrupts unmasked or acknowledge the wrong channel.

Test signals: compile coverage through `pxafb.c`, static comparison against hardware reference manuals, and hardware tests for panel enable/disable, timing, palette DMA, panning branch registers, overlay enable/disable branch completions, smart-panel command completion, and IRQ status clearing.
