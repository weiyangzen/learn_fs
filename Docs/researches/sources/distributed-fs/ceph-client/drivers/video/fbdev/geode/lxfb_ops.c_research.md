<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_ops.c -->
## sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_ops.c

Purpose: contains Geode LX hardware operations for dot-clock programming, mode programming, output enable/disable sequencing, palette writes, blanking, and suspend/resume register save/restore.

Important APIs, types, and functions: `pll_table` maps dot-clock frequencies to PLL values. `lx_set_dotpll()` writes `MSR_GLCP_DOTPLL` and waits for lock. `lx_set_clock()` chooses the closest PLL entry from `info->var.pixclock`. `lx_graphics_disable()` shuts down video overlays, VGA/video enable, IRQs, genlock, color key, panel power, DACs, display timing generator, FIFO loader, and waits for GP idle. `lx_graphics_enable()` programs VP display config and panel/CRT output. `lx_framebuffer_size()` obtains VRAM size from GLIU MSR or VSA virtual registers. `lx_set_mode()` programs output MSRs, framebuffer offsets, scaling defaults, DV line size, pitch, watermarks, display timing registers, bpp mode, and re-enables output. `lx_set_palette_reg()` writes DC palette entries. `lx_blank_display()` implements fbdev DPMS. `lx_powerdown()`/`lx_powerup()` call save/disable and restore paths.

Control flow: mode setting unlocks DC registers, disables current graphics, programs clock and output mode, writes frame and timing state, enables graphics, writes main DC config registers, then locks DC. Powerdown waits for idle, snapshots MSRs/registers/palettes/filter coefficient RAM, disables graphics, and marks `powered_down`. Powerup restores PLL, GP/DC/VP/FP state in dependency order and re-enables VP/DC state last.

State and persistence: save/restore persists GP, DC, VP, FP registers, pad/dotpll/display/spare MSRs, DC and VP palettes, horizontal/vertical filter coefficients, and VP coefficient RAM inside `struct lxfb_par`. `powered_down` prevents duplicate transitions. Mode state is otherwise hardware-resident.

Dependencies and integration points: integrated with `lxfb_core.c` callbacks and `lxfb.h` register definitions; uses x86 MSR access, CS5535 VSA helpers, fbdev `fb_info` mode fields, and low-level delays. Output behavior depends on `par->output` flags set by the core.

Risks: busy-wait loops for PLL lock and GP idle can stall if hardware misbehaves; GP idle loops have no timeout in several places. `lx_set_clock()` uses `abs()` on unsigned-derived values and chooses nearest table entry rather than exact validation. Several TODO/FIXME comments mark missing panel scaling, acceleration, interlacing, and compression support. Suspend restore skips selected registers and contains comments questioning some omissions, so obscure hardware state may not round-trip.

Test signals: compare programmed timing registers against expected mode values, verify closest PLL selection for known modes, DPMS blank/unblank on CRT and panel, suspend/resume register round-trip with active palettes and filter state, failure testing for PLL lock/GP busy loops, and visual tests for every supported bpp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/lxfb_ops.c -->
