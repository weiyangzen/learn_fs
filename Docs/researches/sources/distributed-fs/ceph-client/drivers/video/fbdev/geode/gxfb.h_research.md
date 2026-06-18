<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb.h -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb.h

Purpose: declares the Geode GX framebuffer private state, hardware register indexes, bit definitions, MMIO access helpers, and exported operation prototypes shared by `gxfb_core.c`, `video_gx.c`, and `suspend_gx.c`.

Important APIs, types, and functions: `struct gxfb_par` is the central per-device state and includes output policy, MMIO pointers for display/video/graphics processors, `powered_down`, saved MSR state, saved GP/DC/VP/FP registers, and a saved display-controller palette. Prototypes cover framebuffer sizing, pitch calculation, mode programming, hardware palette writes, GX video clock/display/blank operations, and powerdown/powerup. Enums `gp_registers`, `dc_registers`, `vp_registers`, and `fp_registers` name register slots used by inline `read_gp/write_gp`, `read_dc/write_dc`, `read_vp/write_vp`, and `read_fp/write_fp`.

Control flow: this header is not executable by itself. It defines the data contract used when the core driver allocates `fb_info->par`, when the mode code writes display/video registers, and when suspend code snapshots and restores hardware state.

State and persistence: the register count constants define the size of saved state arrays in `struct gxfb_par`. Saved state includes 32-bit register snapshots even for VP/FP areas stored as 64-bit arrays, matching comments that only lower 32 bits are used. MSR persistence covers pad select and dot PLL state.

Dependencies and integration points: includes `<linux/io.h>` and relies on fbdev types through source files that include it. MSR names come from `linux/cs5535.h` and low-level MSR instructions in implementation files. The header ties GX-specific register definitions to the generic fbdev `fb_info` callback flow.

Risks: register offsets and undocumented bits are encoded as constants with sparse comments, so changes require hardware documentation or regression testing. `PREDIV2` is defined with `MSR_GLCP_SYS_RSTPLL_DOTPOSTDIV3`, matching the source but suspicious by name. Inline helpers perform unchecked MMIO arithmetic and assume mappings are valid.

Test signals: compile coverage with all Geode GX files, suspend/resume tests validating saved array sizes against register ranges, and mode/blank tests that exercise every accessor family are the main signals. Static analysis should flag mismatched register-count constants or invalid enum indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/gxfb.h -->
