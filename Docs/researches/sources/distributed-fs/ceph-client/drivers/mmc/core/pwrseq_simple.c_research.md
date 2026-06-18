<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_simple.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_simple.c

## Purpose
`pwrseq_simple.c` implements the generic `mmc-pwrseq-simple` provider for boards that need an external clock and reset GPIOs or reset controller sequencing around MMC power on/off.

## Important APIs, Types, And Functions
Provider state is `struct mmc_pwrseq_simple`, which embeds `struct mmc_pwrseq` and stores `clk_enabled`, post-power-on and power-off delays, optional `ext_clk`, optional reset GPIO array, and optional reset controller. Main callbacks are `mmc_pwrseq_simple_pre_power_on()`, `mmc_pwrseq_simple_post_power_on()`, and `mmc_pwrseq_simple_power_off()`. `mmc_pwrseq_simple_set_gpios_value()` sets all reset GPIOs together using a bitmap.

## Control Flow
Probe allocates state, gets optional `ext_clock`, optionally chooses a shared reset controller when exactly one reset GPIO phandle is present, otherwise falls back to a `reset` GPIO array, reads delay properties, fills the pwrseq fields, and registers the provider. Pre-power-on enables the external clock if present and asserts reset through either reset control or GPIOs. Post-power-on releases reset and waits the configured post-power-on delay. Power-off asserts reset, waits the configured power-off delay, and disables the external clock if it had been enabled.

## State And Persistence
The provider tracks whether the external clock is currently enabled to balance prepare/enable and disable/unprepare calls. It also holds reset descriptors and delay settings for the provider lifetime. Hardware-visible state consists of reset-line assertion/deassertion and external clock state.

## Dependencies And Integration Points
The file depends on platform/OF matching, clock framework, GPIO consumer arrays, bitmap allocation, reset controller APIs, device properties, sleep delays, and the pwrseq registry. It integrates with any MMC host whose device tree references an `mmc-pwrseq-simple` node.

## Risks And Edge Cases
Bitmap allocation failure in GPIO setting silently leaves reset GPIOs unchanged for that callback. Reset-controller use is selected only for a single reset GPIO phandle; multiple reset lines fall back to GPIO control. Optional clock/reset resources may be absent, but real hardware may still require them. Incorrect reset polarity or delay properties can break enumeration. Clock enable errors are not checked in the callback, so a failed clock preparation could leave later enumeration failures as the only symptom.

## Test Signals
Validation should cover providers with only GPIO reset, only reset controller, external clock plus reset, missing optional resources, configured delays, repeated power cycles with balanced clock state, and host enumeration through a matching `mmc-pwrseq-simple` phandle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/pwrseq_simple.c -->
