<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.c

Purpose: Chip-family-specific clock and PLL programming for VIA display engines. It fills a `struct via_clock` function table with operations for primary/secondary display clocks, PLL state, PLL programming, and engine PLL programming.

Important APIs/types/functions: Encoders include `cle266_encode_pll()`, `k800_encode_pll()`, and `vx855_encode_pll()`. Low-level setters program primary, secondary, and engine PLL encoded values through SR registers. State/source helpers include `set_primary_pll_state()`, `set_secondary_pll_state()`, `set_engine_pll_state()`, `set_primary_clock_state()`, `set_secondary_clock_state()`, `set_clock_source_common()`, `set_primary_clock_source()`, and `set_secondary_clock_source()`. `via_clock_init()` selects the correct function table for CLE266/K400, K800-through-VX800, or VX855/VX900, with OLPC overriding display clock state setters to no-ops.

Control flow and state: Runtime callers initialize a `via_clock` object once per chip and then call function pointers during modeset/vclock programming. PLL setters assert reset bits, write encoded multiplier/divisor/rshift bytes, then release reset. Clock/PLL state setters only accept `VIA_STATE_ON` and `VIA_STATE_OFF`; other states are ignored. Undocumented operations log a warning and do not program hardware.

Dependencies and integration points: Depends on `linux/via-core.h`, `via_clock.h`, `global.h`, and `debug.h`. Integrated by chip/modesetting code that needs vclock and engine PLL control. Risks include undocumented dummy handlers for older chips, arithmetic assumptions in PLL encoding, register magic constants, and OLPC-specific no-op behavior to avoid suspend memory corruption. Test signals are pixel-clock accuracy for each chip family, suspend/resume on OLPC XO-1.5, engine acceleration after engine PLL programming, and no warnings on documented paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_clock.c -->
