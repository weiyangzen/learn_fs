<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/share.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/share.h

Purpose: Common VIA register, bit, display-path, color-depth, output-interface, hardware-layout, CRTC index, LCD method, and small shared type definitions. This is the low-level symbolic map for legacy VGA-style sequencer, CRTC, graphics-controller, DAC, and LCD registers.

Important APIs/types/functions: Defines `BIT0` through `BIT7`, standard table lengths (`StdCR`, `StdSR`, `StdGR`, `StdAR`), IGA identifiers, mode-depth flags, large lists of `SR*` and `CR*` register indices, DAC/LUT ports, logical device constants, output-interface constants (`INTERFACE_DVP0`, `INTERFACE_DFP_LOW`, `INTERFACE_LVDS0LVDS1`, etc.), hardware layouts, CRTC timing indexes, LCD display method constants, `struct crt_mode_table`, and `struct io_reg`.

Control flow and state: No executable flow. The values are consumed by table-driven register writes in `viamode.c`, `hw.c`, `lcd.c`, `viafbdev.c` procfs handlers, and utility/gamma code. State and persistence are hardware state in indexed registers and in static mode tables that refer to these constants.

Dependencies and integration points: Includes `via_modesetting.h` so `struct crt_mode_table` can embed `struct via_display_timing`. It is a foundational dependency for almost every file in `drivers/video/fbdev/via`. Risks are namespace pollution from generic names like `BIT0`, typoed/legacy constants (`LCD_EXPANDSION`), and the lack of type separation between register indices, masks, and values. Test signals are compile coverage, register table application checks, and hardware smoke tests after any register constant change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/share.h -->
