<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-hibvt.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-hibvt.c

Purpose: provides PWM support for HiSilicon BVT SoCs, programming per-channel period, duty, polarity, keep, and enable bits in MMIO register blocks.

Important APIs/types/functions: `struct hibvt_pwm_chip` carries the clock, MMIO base, reset control, and SoC descriptor; `struct hibvt_pwm_soc` supplies channel count and a `quirk_force_enable` flag. `hibvt_pwm_config()`, `hibvt_pwm_set_polarity()`, `hibvt_pwm_enable()`, `hibvt_pwm_disable()`, `hibvt_pwm_get_state()`, and `hibvt_pwm_apply()` are the functional callbacks around `hibvt_pwm_set_bits()`.

Control flow: probe allocates `npwm` channels from match data, gets and enables the clock, maps registers, obtains reset control, toggles reset, registers the chip, and sets the KEEP bit on every channel. Apply updates polarity, then period/duty if changed, performs a second enable for quirked SoCs when refreshing an enabled duty, and finally toggles enable state.

State and persistence: period and duty are programmed as raw clock-derived counts in `PWM_CFG0/1`, with polarity/enable/keep in `PWM_CTRL`. The driver keeps no software cache; `get_state()` reconstructs values from registers and current clock rate. Remove unregisters the chip, resets the block, and disables the clock.

Dependencies and integration: depends on platform/OF matching, the common clock framework, reset controls, MMIO accessors, and PWM core callbacks. SoC data covers `hi3516cv300`, `hi3519v100`, `hi3559v100-shub`, and `hi3559v100`.

Risks and test signals: arithmetic uses MHz-scale clock conversion and 32-bit register fields, so low clock rates, zero period, or extreme periods deserve testing. There is no explicit locking around read-modify-write operations. Test probe/remove reset sequencing, quirked double-enable behavior, polarity changes while enabled, and `get_state()` round-trip accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-hibvt.c -->
