<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-meson.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-meson.c

Purpose: drives Amlogic Meson PWM blocks, which combine per-channel mux/divider/gate clock controls with high/low counters in two output registers. It supports legacy clock-name bindings, v2 index-based bindings, and S4-style externally provided clocks.

Important APIs/types/functions: `struct meson_pwm` stores SoC data, two `meson_pwm_channel` instances, MMIO base, and a spinlock protecting shared `REG_MISC_AB`. `meson_pwm_calc()`, `meson_pwm_enable()`, `meson_pwm_disable()`, `meson_pwm_apply()`, and `meson_pwm_get_state()` implement PWM ops. Channel initialization is split into `meson_pwm_init_clocks_meson8b_*()` and `meson_pwm_init_channels_s4()`.

Control flow: probe maps registers, initializes the spinlock, selects SoC data, initializes per-channel clocks, and registers two PWMs. Request enables the selected channel clock. Apply records polarity, handles disabled inverted output specially on old hardware without polarity support, or computes clock rate/high/low counts, sets clock rate, writes count and enable/constant/invert bits under the spinlock. Get-state reads the shared misc and channel count registers and derives period/duty from channel clock rate.

State and persistence: per-channel software caches desired rate, high/low counts, constant-output flag, and inverted flag; hardware registers store active counts and enable bits. Legacy hardware cannot accurately read back emulated inverted polarity, which is documented in the source comments.

Dependencies and integration: depends on platform/OF, clk provider APIs for registering mux/divider/gate clocks, raw OF clock gets for S4, spinlocks, MMIO, and PWM core. Many compatible strings select parent names and feature flags.

Risks and test signals: polarity behavior differs by hardware generation, and older emulation intentionally makes get-state imperfect. Shared `REG_MISC_AB` updates must stay locked against clock framework operations. Test legacy and v2 bindings, S4 clock cleanup, constant 0/100% duty, inverted disabled state, clock-rate rounding, and concurrent two-channel updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-meson.c -->
