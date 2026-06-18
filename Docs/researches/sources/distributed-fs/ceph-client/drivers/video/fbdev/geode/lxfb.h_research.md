<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb.h

Purpose: provides the Geode LX framebuffer private state, output flags, register index maps, bit definitions, MMIO helpers, and operation prototypes shared by the LX core and operations files.

Important APIs, types, and functions: `struct lxfb_par` carries output mask, GP/DC/VP MMIO pointers, `powered_down`, saved MSR values, register snapshots, palettes, filter coefficients, and VP coefficient RAM. `lx_get_pitch()` aligns scanline pitch to 8 bytes. Public prototypes include `lx_set_mode()`, `lx_framebuffer_size()`, `lx_blank_display()`, `lx_set_palette_reg()`, `lx_powerdown()`, and `lx_powerup()`. Enums define GP, DC, VP, and FP register indexes; inline accessors map those indexes to byte offsets in MMIO.

Control flow: like `gxfb.h`, this file is a contract, not a standalone driver. The core initializes `struct lxfb_par`, `lxfb_ops.c` consumes register constants to program clocks and display state, and suspend code uses the arrays and MSR members to save/restore hardware.

State and persistence: compared with GX, LX preserves more state: DC and VP palettes, horizontal and vertical filter coefficients, and video processor coefficient RAM. Output state uses `OUTPUT_CRT` and `OUTPUT_PANEL` bit flags rather than the GX boolean CRT flag.

Dependencies and integration points: depends on fbdev type declarations and LX/CS5535 MSR definitions in implementation files. It integrates MMIO registers, MSR control, flat-panel registers at `VP_FP_START`, and fbdev palette/mode callbacks.

Risks: many MSR bits are documented in comments as undocumented or uncertain, so hardware compatibility depends on legacy knowledge. Inline accessors are unchecked and depend on successful BAR mappings. The state arrays must remain consistent with register counts or suspend/resume will silently omit or overrun intended state.

Test signals: build tests with `lxfb_core.c` and `lxfb_ops.c`, mode-setting smoke tests for CRT, panel, and simultaneous output, suspend/resume state comparison on representative hardware, and static checks for register enum values exceeding count constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb.h -->
