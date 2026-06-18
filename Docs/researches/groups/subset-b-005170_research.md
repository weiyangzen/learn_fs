# subset-b-005170 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-fsl-ftm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-fsl-ftm.c

Purpose: implements the Freescale/NXP FlexTimer Module PWM provider for VF610, i.MX8QM, and S32G2-style FTM blocks. It exposes up to eight PWM channels, but the controller has one shared period source, so the driver arbitrates period-clock and prescaler changes across all enabled outputs.

Important APIs/types/functions: `struct fsl_pwm_chip` holds the regmap, clocks, SoC data, and current shared `struct fsl_pwm_periodcfg`. `fsl_pwm_request()` and `fsl_pwm_free()` manage the interface clock and optional channel enable bits. `fsl_pwm_calculate_period()`, `fsl_pwm_apply_config()`, and `fsl_pwm_apply()` implement period selection, duty programming, polarity, output masking, and counter-clock enable/disable. Probe uses `devm_regmap_init_mmio_clk()`, named clocks `ftm_sys`, `ftm_fix`, `ftm_ext`, `ftm_cnt_clk_en`, optional `ipg`, and SoC match data.

Control flow: probe maps registers, builds a regmap with volatile/readable/writeable filters, gets clocks, registers the PWM chip, and initializes counter start, output init, and output masks. Applying an enabled state computes the best source clock and prescaler, rejects shared-period changes while other PWMs are enabled, clears FTM write protection, updates `FTM_SC`, `FTM_MOD`, channel status/value registers, and polarity, then unmasks the output after enabling the selected period clock and counter-enable clock. Disabling masks the channel and drops enabled clocks.

State and persistence: hardware registers and clock enables hold runtime state. The driver caches only the active shared period config; it is valid when at least one PWM is running. Suspend moves regmap into cache-only dirty mode and disables requested/enabled clocks; resume reenables clocks for requested/enabled channels and syncs the cached register image. No state is persisted outside hardware/kernel memory.

Dependencies and integration: depends on Linux PWM core, platform/OF binding, clk framework, regmap MMIO cache, PM sleep hooks, and `linux/fsl/ftm.h` register definitions. It integrates with consumers through standard `pwm_ops` and with SoC variants through `struct fsl_ftm_soc`.

Risks and test signals: the shared period is the main behavioral constraint; tests should cover two channels with conflicting periods, period source changes, enable/disable clock reference balance, and SoC variants with/without enable bits and filter registers. The duplicated `if (!fsl_pwm_is_any_pwm_enabled(...))` in `fsl_pwm_apply_config()` is suspicious style and should be reviewed for intended control flow. Test suspend/resume with enabled outputs and regcache sync failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-fsl-ftm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-gpio.c

Purpose: implements a software PWM generator using one non-sleeping GPIO and an hrtimer. It is useful for simple GPIO-backed modulation where hardware PWM is unavailable and atomic GPIO access is possible.

Important APIs/types/functions: `struct pwm_gpio` stores the GPIO descriptor, current and pending `pwm_state`, hrtimer, spinlock, and timer flags. `pwm_gpio_round()` quantizes requested period/duty to `hrtimer_resolution`; `pwm_gpio_toggle()` writes the GPIO and schedules the next edge; `pwm_gpio_timer()` applies pending state changes at period boundaries. `pwm_gpio_apply()` and `pwm_gpio_get_state()` implement PWM core callbacks.

Control flow: probe acquires one GPIO as `GPIOD_ASIS`, rejects `gpiod_cansleep()` GPIOs, initializes an hrtimer and atomic PWM chip, and registers cleanup to cancel the timer. Apply validates that nonzero high/low phases are at least one hrtimer tick, starts the GPIO as output when needed, and either disables immediately, queues a next-state update for the end of the current period, or starts the timer from an idle state.

State and persistence: all state is in `struct pwm_gpio`; there is no hardware persistence beyond the current GPIO output level. The spinlock protects timer and pwm_ops state. `changing` tells `get_state()` to report the pending state, and `running` distinguishes continuous toggling from fixed 0/100% outputs.

Dependencies and integration: depends on the PWM core, GPIO consumer API, hrtimers, spinlocks, platform/OF matching for `pwm-gpio`, and non-sleeping GPIO controllers. It sets `chip->atomic = true`, so apply paths must remain IRQ-safe once the GPIO direction has been configured.

Risks and test signals: timing quality is bounded by hrtimer latency and scheduler/IRQ behavior, not hardware precision. Sleeping GPIOs are rejected because timer callbacks cannot sleep. Tests should cover 0%, 100%, inverted polarity, very small duty/low phases, state changes while running, hrtimer cancellation on remove, and GPIO value behavior after disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-hibvt.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-hibvt.c

Purpose: provides PWM support for HiSilicon BVT SoCs, programming per-channel period, duty, polarity, keep, and enable bits in MMIO register blocks.

Important APIs/types/functions: `struct hibvt_pwm_chip` carries the clock, MMIO base, reset control, and SoC descriptor; `struct hibvt_pwm_soc` supplies channel count and a `quirk_force_enable` flag. `hibvt_pwm_config()`, `hibvt_pwm_set_polarity()`, `hibvt_pwm_enable()`, `hibvt_pwm_disable()`, `hibvt_pwm_get_state()`, and `hibvt_pwm_apply()` are the functional callbacks around `hibvt_pwm_set_bits()`.

Control flow: probe allocates `npwm` channels from match data, gets and enables the clock, maps registers, obtains reset control, toggles reset, registers the chip, and sets the KEEP bit on every channel. Apply updates polarity, then period/duty if changed, performs a second enable for quirked SoCs when refreshing an enabled duty, and finally toggles enable state.

State and persistence: period and duty are programmed as raw clock-derived counts in `PWM_CFG0/1`, with polarity/enable/keep in `PWM_CTRL`. The driver keeps no software cache; `get_state()` reconstructs values from registers and current clock rate. Remove unregisters the chip, resets the block, and disables the clock.

Dependencies and integration: depends on platform/OF matching, the common clock framework, reset controls, MMIO accessors, and PWM core callbacks. SoC data covers `hi3516cv300`, `hi3519v100`, `hi3559v100-shub`, and `hi3559v100`.

Risks and test signals: arithmetic uses MHz-scale clock conversion and 32-bit register fields, so low clock rates, zero period, or extreme periods deserve testing. There is no explicit locking around read-modify-write operations. Test probe/remove reset sequencing, quirked double-enable behavior, polarity changes while enabled, and `get_state()` round-trip accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-hibvt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-img.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-img.c

Purpose: implements the Imagination Technologies Pistachio PWM DAC controller with four channels, per-channel timebase/duty registers, shared divider control, peripheral PDM mux clearing, runtime PM, and sleep-state save/restore.

Important APIs/types/functions: `struct img_pwm_chip` stores `sys` and `pwm` clocks, MMIO base, peripheral syscon regmap, period bounds, SoC max timebase, and suspend shadows. `img_pwm_config()`, `img_pwm_enable()`, `img_pwm_disable()`, and `img_pwm_apply()` are the PWM operations. PM callbacks are `img_pwm_runtime_suspend/resume()` and system `img_pwm_suspend/resume()`.

Control flow: probe maps the PWM block, looks up the `img,cr-periph` syscon, enables runtime PM, validates the PWM clock rate, computes min/max period bounds, and registers four PWMs. Apply rejects inverted polarity, validates period range, computes divider and timebase among no-div, /8, /64, and /512 modes, writes channel config under runtime PM, and enables the channel by setting `PWM_CTRL_CFG` plus clearing the peripheral PDM-control bit.

State and persistence: runtime state is in channel config registers and `PWM_CTRL_CFG`; the driver keeps min/max period metadata and suspend shadow copies. Runtime suspend disables both clocks. System suspend forces a resume if necessary, snapshots all channel config and control registers, then suspends clocks; resume restores registers and PDM mux state for enabled channels.

Dependencies and integration: depends on OF/platform probing, clk, regmap syscon, runtime PM autosuspend, PWM core, and Pistachio match data. It integrates with SoC pin/peripheral routing through the syscon phandle.

Risks and test signals: no `.get_state()` means consumers cannot read back actual rounded state through this driver. PM ordering is delicate because register reads/writes need clocks. Test period min/max boundaries, each divider bucket, PDM mux clearing after enable and resume, autosuspend behavior, and removal when runtime PM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-img.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx-tpm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx-tpm.c

Purpose: supports the NXP i.MX TPM PWM block, where the counter and period register are shared by all channels and each channel has its own mode/status and compare value.

Important APIs/types/functions: `struct imx_tpm_pwm_chip` tracks clock, MMIO base, mutex, `user_count`, `enable_count`, and cached `real_period`. `pwm_imx_tpm_round_state()` computes prescale/MOD/CnV values and the actual hardware state. `pwm_imx_tpm_apply_hw()` serializes shared counter updates, polarity, duty, and enable-count logic. `request/free`, `get_state`, and PM suspend/resume complete the PWM core interface.

Control flow: probe maps registers, enables the clock, reads `PWM_IMX_TPM_PARAM_CHAN` for channel count, initializes the mutex, counts already enabled channels, and registers the chip. Apply rounds the requested state, locks, rejects period changes when more than one user exists or when an active counter would need a prescale change, updates prescale/MOD/CnV, waits for latched values, refuses polarity changes on active channels, then updates channel mode bits and starts/stops the shared counter based on `enable_count`.

State and persistence: `real_period` is a software cache because the shared period is not per-channel. `user_count` and `enable_count` coordinate shared resources. Hardware registers hold actual channel status. Suspend refuses if any channel is enabled, zeros `real_period` so resume forces reprogramming, disables the clock, and switches pinctrl to sleep; resume selects default pinctrl and reenables the clock.

Dependencies and integration: depends on platform/OF, clk, pinctrl PM states, mutexes, MMIO, jiffies timeouts, and PWM core. Its behavior is constrained by TPM hardware latching semantics.

Risks and test signals: shared period semantics can surprise consumers; period/prescale changes should be tested with multiple requested channels. Busy-wait latching is timeout-sensitive and uses `real_period` for timeout sizing. Test active polarity rejection, suspend `-EBUSY`, enabled-channel count after bootloader state, very small periods, and register latch timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx-tpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx1.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx1.c

Purpose: provides a minimal PWM driver for early i.MX1/i.MX21-style PWM hardware, primarily preserving bootloader-programmed period settings and adjusting duty ratio.

Important APIs/types/functions: `struct pwm_imx1_chip` stores IPG/peripheral clocks and MMIO base. `pwm_imx1_config()` reads `MX1_PWMP` and writes `MX1_PWMS`; `pwm_imx1_enable()` and `pwm_imx1_disable()` manage clocks and `MX1_PWMC_EN`; `pwm_imx1_apply()` provides the PWM callback.

Control flow: probe gets `ipg` and `per` clocks, maps registers, sets ops, and registers one PWM. Apply rejects inverted polarity, disables by clearing enable and dropping clocks, or computes sample register value from requested duty/period and enables clocks plus the control bit when transitioning from disabled.

State and persistence: the driver does not program the hardware period or prescaler; it relies on existing `MX1_PWMP` state and only changes the sample register and enable bit. It keeps no software cache and has no PM callbacks.

Dependencies and integration: depends on platform/OF, clk framework, MMIO, and PWM core. It is intentionally simple and backlight-oriented rather than a full frequency-programming driver.

Risks and test signals: period requests are not actually honored if they differ from bootloader setup. No `.get_state()` exists. Test duty ratio behavior against an already configured PWM period, clock enable/disable balance, polarity rejection, and bootloader/default register assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx27.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx27.c

Purpose: implements the i.MX27-and-newer single-channel PWM controller, including period/duty programming, clock management, polarity, state readback, FIFO handling, and a documented erratum workaround.

Important APIs/types/functions: `struct pwm_imx27_chip` stores bulk clocks, MMIO base, and cached duty for disabled readback. `pwm_imx27_get_state()`, `pwm_imx27_sw_reset()`, `pwm_imx27_wait_fifo_slot()`, and `pwm_imx27_apply()` are the core routines. Register definitions cover `PWMCR`, `PWMSR`, `PWMSAR`, `PWMPR`, and `PWMCNR`.

Control flow: probe gets `ipg` and `per` clocks, maps registers, temporarily enables clocks to detect boot-enabled PWM state, and keeps them on only if already running. Apply computes prescale, period, and duty cycles from `per` clock, resets FIFO when enabling from disabled, waits for a FIFO slot when already enabled, applies ERR051198 workaround around decreasing duty with local IRQs disabled, writes sample and period registers, caches duty, and writes the control register with polarity and enable bits.

State and persistence: enabled hardware keeps clocks prepared. The driver caches `duty_cycle` because `PWMSAR` cannot be read while disabled. Register state persists only while hardware remains powered; no explicit system PM hooks are present here.

Dependencies and integration: depends on bulk clocks, platform/OF, MMIO, PWM core, local IRQ masking, and timing helpers. It integrates with PWM consumers as a one-channel provider.

Risks and test signals: the FIFO/erratum path is timing-sensitive, especially high-frequency PWM and decreasing duty updates. Test enabled-to-enabled duty changes, disabled readback, inverted polarity, very small and maximum periods (`PWMPR_MAX`), probe with boot-enabled hardware, and warning paths for full FIFO or reset timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-intel-lgm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-intel-lgm.c

Purpose: drives the Intel Lightning Mountain dedicated fan PWM controller. The hardware exposes one fixed-period, normal-polarity, two-wire fan PWM output with duty stored in an 8-bit field and max-RPM configuration.

Important APIs/types/functions: `struct lgm_pwm_chip` stores the regmap and fixed period. `lgm_pwm_apply()`, `lgm_pwm_get_state()`, `lgm_pwm_enable()`, and `lgm_pwm_init()` implement the PWM behavior. Probe uses MMIO regmap, a clock, reset control, and devm cleanup actions for clock disable and reset assert.

Control flow: probe maps registers, initializes regmap, enables the clock, deasserts reset, initializes mode to two-wire and default max RPM, then registers one PWM. Apply rejects non-normal polarity and periods shorter than the fixed 40 ms period, writes scaled duty into `LGM_PWM_FAN_CON0`, and toggles enable. Get-state reads enable and duty fields and reports the fixed period.

State and persistence: runtime state is in fan controller registers; software only stores `period`. Device-managed actions assert reset and disable the clock on teardown. There is no suspend/resume logic in this file.

Dependencies and integration: depends on platform/OF, clk, reset controller, regmap MMIO, and PWM core. It is intended for fan-control consumers rather than arbitrary PWM waveform generation.

Risks and test signals: consumers requesting a shorter period or inverted polarity will fail. Duty changes may affect the first period immediately. Test fixed-period acceptance, duty scaling endpoints, reset/clock cleanup, get-state readback, and fan controller mode/max-RPM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-intel-lgm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-iqs620a.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-iqs620a.c

Purpose: exposes the Azoteq IQS620A MFD PWM generator on GPIO3/LTX as a one-channel, fixed-1 ms PWM provider backed by parent regmap registers and reset notifications.

Important APIs/types/functions: `struct iqs620_pwm_private` stores parent `iqs62x_core`, mutex, notifier, and cached `duty_scale`. `iqs620_pwm_init()` writes duty or disables PWM output; `iqs620_pwm_apply()` validates fixed-period/normal polarity and updates hardware; `iqs620_pwm_get_state()` reports cached state; `iqs620_pwm_notifier()` restores PWM configuration after parent device reset.

Control flow: probe retrieves parent MFD data, reads current enable/duty state, initializes the mutex, registers a blocking notifier on the parent reset chain, adds devm cleanup to unregister it, and registers one PWM. Apply clamps duty to 1 ms, maps it to 0..256 scale, uses zero scale to disable output, and updates cached state under lock after successful regmap writes.

State and persistence: hardware holds the duty register and PWM output bit, while `duty_scale` is the software source of truth for get-state and reset restore. No nonvolatile persistence is provided. Parent reset events require reinitialization from the cached scale.

Dependencies and integration: depends on the IQS62x MFD core, parent regmap, blocking notifier chain, mutex, platform device created by the MFD, and PWM core.

Risks and test signals: the hardware cannot generate true 0% while enabled, so low duty is represented by disabling output and relying on an external pull-down. Test reset notifier restore, initial hardware state import, 0/1/255/256 scale boundaries, fixed-period rejection, polarity rejection, and notifier unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-iqs620a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-jz4740.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-jz4740.c

Purpose: provides PWM support for Ingenic JZ4740/JZ4725B/X1000 TCU timer channels using the parent TCU regmap and per-channel timer clocks.

Important APIs/types/functions: `struct jz4740_pwm_chip` stores the TCU regmap and an array of per-channel clocks; `struct soc_info` supplies channel count. `jz4740_pwm_request()` enforces the `ingenic,pwm-channels-mask` property and gets `timerN` clocks. `jz4740_pwm_apply()` computes clock rate, period, duty, polarity/init level, and enables/stops the TCU channel.

Control flow: probe gets match data, allocates flexible clock storage, obtains the parent TCU regmap, and registers the PWM chip. Request gets and enables a timer clock. Apply rounds the clock rate down through `clk_round_rate()`, disables the channel, sets the new rate, resets the counter, writes duty and period registers, sets abrupt shutdown and initial level according to polarity/enabled state, then starts the counter if enabled. Free disables and releases the timer clock.

State and persistence: hardware TCU registers hold period, duty, counter, PWM mode, and enable state. The driver stores only per-request clock pointers. There is no get-state or PM restore in this file.

Dependencies and integration: depends on the Ingenic TCU MFD register map, syscon/regmap, named timer clocks, platform/OF matching, device properties on the parent, and PWM core.

Risks and test signals: the code assumes Ingenic clock `clk_round_rate()` rounds down, which is not guaranteed by the generic clk API. Channel mask handling can conflict with TCU users. Test masked channel rejection, all SoC channel counts, clock-rate rounding, full-duty clamp (`duty >= period`), polarity behavior, and apply while running because it does not wait for the current period to finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-jz4740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-keembay.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-keembay.c

Purpose: implements Intel Keem Bay six-channel PWM hardware, where each channel has a lead-in register with enable bit and a high/low count register with 16-bit high and low phases.

Important APIs/types/functions: `struct keembay_pwm` stores the MMIO base, clock, and clock-rate-derived nanosecond scale. `keembay_pwm_get_state()` decodes enable/high/low counts; `keembay_pwm_apply()` computes 16-bit high and low counts from requested period/duty and writes channel registers; small helpers manage enable bits and clock lifetime.

Control flow: probe maps registers, gets/enables the clock with devm cleanup, stores clock rate, and registers six PWMs. Apply rejects inverted polarity, disables when requested, otherwise computes high count from duty and low count from period minus duty, rejects values above `U16_MAX`, writes high/low fields, and sets the enable bit. Get-state reconstructs duty and period from counts and cached clock rate.

State and persistence: hardware registers hold enable and high/low counts; the software cache is only the input clock rate. No suspend/resume is implemented, so power-domain reset would require consumers to reapply state.

Dependencies and integration: depends on platform/OF, clk, MMIO, bitfield helpers, and PWM core. It is a straightforward fixed-clock counter backend.

Risks and test signals: period and duty limits are hard 16-bit count limits. Clock-rate changes after probe are not tracked. Test 0%, 100%, max-count periods, polarity rejection, get-state round trips, and clock cleanup on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-keembay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-loongson.c

Purpose: drives Loongson PWM registers for a single-channel counter with duty, period, control, polarity inversion, and enable/output-control bits.

Important APIs/types/functions: `struct pwm_loongson_ddata` stores MMIO base, clock frequency, and suspend shadow registers. `pwm_loongson_config()`, `pwm_loongson_set_polarity()`, `pwm_loongson_enable()`, `pwm_loongson_disable()`, `pwm_loongson_apply()`, and `pwm_loongson_get_state()` implement the PWM behavior. Probe supports OF and ACPI IDs and reads `clock-frequency`, defaulting to 50 MHz.

Control flow: probe maps MMIO, reads clock frequency from firmware properties, and registers one PWM. Apply optionally changes polarity, disables when needed, computes period/duty counts from the configured frequency, writes duty and period, and enables output/counter. Suspend saves duty/period/control and disables the PWM; resume restores the saved registers.

State and persistence: hardware registers hold runtime state. The driver shadows `duty`, `period`, and `ctrl` across system sleep only. There is no clock framework integration; the frequency property is assumed static.

Dependencies and integration: depends on platform bus, ACPI/OF matching, device properties, MMIO access, PM sleep ops, and PWM core.

Risks and test signals: wrong `clock-frequency` directly skews all periods and duty cycles. Control bit `OE` is active-low by hardware comment, so enable/disable polarity deserves hardware validation. Test OF and ACPI probe, suspend/resume restore, inverted polarity, frequency defaulting, and max/min count conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lp3943.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lp3943.c

Purpose: exposes the TI/National LP3943 LED driver’s two PWM generators as PWM providers while coordinating pin mux ownership with LP3943 GPIO/LED functions.

Important APIs/types/functions: `struct lp3943_pwm` stores the parent `lp3943` device, pin maps, period, and duty values. `lp3943_pwm_request()` maps a PWM to available LP3943 output pins parsed from `ti,pwmX` child properties. `lp3943_pwm_config()`, `lp3943_pwm_set_mode()`, `lp3943_pwm_enable()`, `lp3943_pwm_disable()`, and `lp3943_pwm_apply()` program parent regmap state.

Control flow: probe parses DT child nodes to build per-PWM pin maps, stores parent MFD data, and registers two PWMs. Request claims the mapped pins from the LP3943 mux map. Apply rejects unsupported polarity, computes LP3943 prescale/duty fields within 6.25 us to 1.6 ms period limits, writes period and duty registers, and switches mapped output pins between PWM mode and input/high-Z/disabled mode as enable changes.

State and persistence: software caches period and duty per PWM because mapping and register programming are per generator. Parent regmap registers and pin mux bits hold runtime hardware state; no system PM handling exists here.

Dependencies and integration: depends on LP3943 MFD structures, parent regmap, OF child properties, PWM core, and the shared LP3943 mux map used by sibling functions.

Risks and test signals: pin mapping conflicts are the key integration risk. Test DT parsing for `ti,pwm0`/`ti,pwm1`, request/free conflict handling, period bounds, multiple mapped pins per PWM, enable/disable mode changes, and parent MFD removal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lp3943.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc18xx-sct.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc18xx-sct.c

Purpose: implements PWM output on the NXP LPC18xx State Configurable Timer by using SCT match/events/output set-clear resources. It exposes 16 PWM outputs with one shared period event.

Important APIs/types/functions: `struct lpc18xx_pwm_chip` stores base, clock, rate, period, and an array of per-channel enabled state. Helpers include `lpc18xx_pwm_config_period()`, `lpc18xx_pwm_config_duty()`, `lpc18xx_pwm_enable()`, `lpc18xx_pwm_disable()`, `request/free`, and `apply`. Register macros cover config/control, match/matchrel, event control/masks, output set/clear, and conflict resolution.

Control flow: probe enables the clock, configures the SCT as unified unidirectional counter, initializes period event 0, sets output conflict behavior, and registers 16 PWMs. Request configures a channel event and default duty. Apply reprograms the shared period when necessary, updates duty match for the channel, then enables/disables output actions according to state and polarity.

State and persistence: period is cached in the driver because it is shared. Hardware match/event/output registers hold channel state. Per-channel `enabled` flags track requested output state for shared period changes. Remove unregisters the chip and disables the clock.

Dependencies and integration: depends on platform/OF, clock framework, MMIO, PWM core, and SCT hardware resource mapping where event 0 is reserved for period and channels use subsequent events.

Risks and test signals: shared-period changes can affect all channels, and event allocation is fixed. Test multiple enabled outputs, polarity changes, 0/100% duty, maximum timer values, request/free resource cleanup, and clock-rate-derived period rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc18xx-sct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc32xx.c

Purpose: provides a simple one-channel PWM driver for LPC32xx, programming one combined control register with enable, pin level, duty, and period-derived fields.

Important APIs/types/functions: `struct lpc32xx_pwm_chip` stores clock and MMIO base. `lpc32xx_pwm_config()`, `lpc32xx_pwm_enable()`, `lpc32xx_pwm_disable()`, and `lpc32xx_pwm_apply()` form the PWM implementation.

Control flow: probe maps the register block, gets the clock, and registers one PWM. Apply rejects inverted polarity, disables by clearing enable and dropping the clock, or enables the clock, computes register fields from requested period/duty and clock rate, writes configuration, and sets enable.

State and persistence: hardware register contents and clock enable are the only runtime state; the driver keeps no cache and provides no `.get_state()`. The disabled output is controlled through the configured pin-level bit.

Dependencies and integration: depends on OF/platform probing, clk framework, MMIO, and PWM core. It targets `nxp,lpc3220-pwm`.

Risks and test signals: without get-state or PM hooks, state recovery is limited. Test clock enable/disable balance, period/duty conversion at extremes, disabled output level, polarity rejection, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpc32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-pci.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-pci.c

Purpose: is the PCI front-end for Intel LPSS PWM controllers. It binds PCI IDs, maps BAR0, selects board info, and delegates all waveform logic to the shared LPSS core.

Important APIs/types/functions: `pwm_lpss_probe_pci()` enables the PCI device, ioremaps BAR0 through `pcim_iomap_regions()`, calls `devm_pwm_lpss_probe()`, and stores the returned chip. `pwm_lpss_remove_pci()` calls `pwm_lpss_remove()`. The ID table maps Bay Trail, Braswell, Broxton, and Tangier device IDs to exported `pwm_lpss_*_info` descriptors.

Control flow: module PCI probe performs managed PCI enable/mapping and shared-core registration. Remove asks the LPSS core to stop/remove any registered PWM chip state.

State and persistence: this file owns no waveform state. PCI core and shared `struct pwm_lpss_chip` hold runtime state after probe.

Dependencies and integration: depends on PCI APIs, LPSS shared core and header, module namespace import `PWM_LPSS`, and Intel LPSS device IDs.

Risks and test signals: wrong ID-to-boardinfo mapping changes period limits and channel count. Test each supported PCI ID, BAR mapping failure, remove/unbind while PWM is enabled, and namespace/export linkage with `pwm-lpss.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-platform.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-platform.c

Purpose: is the ACPI/platform front-end for Intel LPSS PWM controllers. It maps a platform resource, selects board info from ACPI IDs or platform data, and delegates to the shared LPSS PWM core.

Important APIs/types/functions: `pwm_lpss_probe_platform()` resolves `struct pwm_lpss_boardinfo`, maps resource 0 with `devm_platform_ioremap_resource()`, and calls `devm_pwm_lpss_probe()`. The ACPI table maps `80860F09`, `80862288`, and `80862289` to LPSS variants.

Control flow: platform probe prefers ACPI match data when an ACPI companion exists, otherwise uses `dev_get_platdata()`. After MMIO mapping, all PWM registration and runtime behavior are handled by `pwm-lpss.c`.

State and persistence: no local PWM state is stored here. The shared LPSS core stores register base and boardinfo in its chip-private structure.

Dependencies and integration: depends on platform bus, ACPI matching, LPSS shared exports in namespace `PWM_LPSS`, and PWM core indirectly through `devm_pwm_lpss_probe()`.

Risks and test signals: missing platform data on non-ACPI devices returns `-ENODEV`. Test ACPI and platform-data probe paths, resource-map failures, ID mapping, and module namespace/import behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.c

Purpose: implements the shared Intel LPSS PWM core used by both PCI and platform front-ends. It programs LPSS PWM registers with an enable bit, software-update bit, base-unit field, and on-time divider.

Important APIs/types/functions: exported board descriptors `pwm_lpss_byt_info`, `pwm_lpss_bsw_info`, `pwm_lpss_bxt_info`, and `pwm_lpss_tng_info` define clock rate, npwm, base-unit constraints, and bypass behavior. `struct pwm_lpss_chip` is allocated by `devm_pwm_lpss_probe()`. Core functions include `pwm_lpss_prepare()`, `pwm_lpss_prepare_enable()`, `pwm_lpss_wait_for_update()`, `pwm_lpss_apply()`, `pwm_lpss_get_state()`, and `pwm_lpss_remove()`.

Control flow: front-ends call `devm_pwm_lpss_probe()` with MMIO base and boardinfo; it allocates a PWM chip, stores base/info, sets ops, and registers the chip. Apply computes base-unit and on-time fields from requested state, handles fixed/bypass variants, writes the register with software-update, waits for update completion when required, and enables/disables the PWM. Get-state decodes the register to report enabled, period, duty, and normal polarity.

State and persistence: each channel state is hardware register state at `PWM_SIZE` spacing. The driver stores base and immutable boardinfo only. `pwm_lpss_remove()` is provided for front-ends that need explicit teardown.

Dependencies and integration: depends on PWM core, IO accessors, exported symbol namespace `PWM_LPSS`, PCI/platform wrappers, and Intel LPSS clock assumptions embedded in boardinfo.

Risks and test signals: timing math is boardinfo-sensitive, especially base-unit ranges and bypass mode. Test Bay Trail/Braswell/Broxton/Tangier descriptors, update timeout behavior, disabled readback, 0/100% duty, and probe/remove from both PCI and platform front-ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.h -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.h

Purpose: declares the shared Intel LPSS PWM core interface consumed by the PCI and platform wrapper drivers.

Important APIs/types/functions: `LPSS_MAX_PWMS` defines the maximum channel count. `struct pwm_lpss_boardinfo` carries per-family clock rate, channel count, base-unit bit width, fixed base-unit value, and bypass flag. It declares exported descriptors for BYT, BSW, BXT, and TNG plus `devm_pwm_lpss_probe()` and `pwm_lpss_remove()`.

Control flow: the header has no runtime control flow; it defines the contract wrappers use to instantiate the common core.

State and persistence: boardinfo data is immutable configuration state. Runtime state is owned by `pwm-lpss.c`.

Dependencies and integration: includes device, IO, and PWM declarations and bridges `pwm-lpss-pci.c`, `pwm-lpss-platform.c`, and `pwm-lpss.c`.

Risks and test signals: interface drift between wrappers and core is the main risk. Compile tests should cover modular builds and namespace import users, plus all boardinfo symbols referenced by PCI/ACPI tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-max7360.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-max7360.c

Purpose: exposes the MAX7360 keypad/GPIO expander PWM outputs through the PWM waveform API. The chip provides eight fixed-period, 8-bit duty PWM channels.

Important APIs/types/functions: `struct max7360_pwm_waveform` stores an 8-bit duty value and enable flag. `max7360_pwm_request()` switches a pin to PWM mode through pinctrl. `max7360_pwm_round_waveform_tohw/fromhw()`, `max7360_pwm_write_waveform()`, and `max7360_pwm_read_waveform()` implement fixed 2 ms period conversion and parent regmap accesses. Probe registers eight PWMs.

Control flow: request looks up and selects a per-channel PWM pinctrl state. Waveform conversion clamps duty to 0..255 over the fixed period and represents zero duty as disabled. Write updates the channel duty register or disables by writing zero; read imports current register value. Probe retrieves parent MAX7360 data and registers the chip.

State and persistence: hardware registers store duty values; pinctrl state controls pin function. The driver keeps no software cache and relies on parent regmap state.

Dependencies and integration: depends on the MAX7360 MFD/regmap, pinctrl states, PWM waveform callbacks, and platform device creation by the parent.

Risks and test signals: missing per-channel pinctrl states prevent channel request. Fixed-period semantics should be tested with consumers that ask for different periods. Test all eight channels, 0/1/255 duty, read/write round trips, pinctrl errors, and parent regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-max7360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mc33xs2410.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mc33xs2410.c

Purpose: implements PWM control for the NXP MC33XS2410 SPI high-side switch. Four switch channels expose frequency, duty, polarity, and enable control through SPI register frames.

Important APIs/types/functions: SPI helpers `mc33xs2410_write_regs()`, `mc33xs2410_read_regs()`, `mc33xs2410_write_reg()`, and `mc33xs2410_read_reg()` encode frame addresses/data. `mc33xs2410_pwm_get_freq()` maps requested periods to chip frequency step/count fields; `mc33xs2410_pwm_get_period()` decodes them. `mc33xs2410_pwm_apply()` and `mc33xs2410_pwm_get_state()` implement PWM ops. `mc33xs2410_reset()` uses optional reset GPIO during probe.

Control flow: probe configures SPI mode, optionally resets the chip, puts global control into normal mode, disables watchdog, allocates four PWM channels, and registers the chip. Apply computes frequency register and duty byte, writes frequency/duty/polarity registers, and toggles per-channel enable. Get-state reads enable, polarity, frequency, and duty registers and reconstructs period/duty.

State and persistence: hardware registers over SPI hold switch state; the driver keeps no cache. State may reset on chip reset or power loss and must be re-applied by consumers.

Dependencies and integration: depends on SPI, GPIO reset, PWM core, bitfield helpers, and module namespace `PWM_MC33XS2410`. It integrates high-side switch outputs into generic PWM consumers.

Risks and test signals: SPI frame packing and multi-transfer limits are central risks. Frequency quantization is coarse and bounded by `MC33XS2410_PWM_MIN_PERIOD`/step max periods. Test SPI read/write error paths, reset timing, watchdog disable, all four channels, duty endpoints, polarity, and get-state after apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mc33xs2410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mediatek.c

Purpose: implements the MediaTek general-purpose PWM controller for many SoCs using the PWM waveform API. It supports multiple channels with top/main/per-channel clocks, SoC-specific register base/stride, optional PWM4/5 register fixups, and optional 26 MHz clock-select clearing.

Important APIs/types/functions: `struct pwm_mediatek_of_data` supplies channel count and register layout. `struct pwm_mediatek_chip` stores MMIO base, top/main clocks, SoC data, and per-channel clock/rate pairs. `pwm_mediatek_round_waveform_tohw/fromhw()`, `pwm_mediatek_read_waveform()`, `pwm_mediatek_write_waveform()`, `pwm_mediatek_clk_enable/disable()`, and `pwm_mediatek_init_used_clks()` are the core routines.

Control flow: probe gets SoC data, maps MMIO, acquires `top`, `main`, and `pwmN` clocks, locks per-channel rates exclusively, preserves clocks for channels already enabled by hardware, and registers the chip. Waveform conversion computes clock divider, 13-bit period, duty threshold, and enable bit from nanoseconds. Write enables clocks, optionally increments the clock usage count when transitioning from disabled to enabled, clears 26 MHz selection when needed, writes channel registers, and disables clocks on transition to off.

State and persistence: hardware registers hold enable, divider, period, and duty. Software caches per-channel clock rates after first use and uses clock prepare counts to keep already-enabled outputs alive. There is no explicit system PM state.

Dependencies and integration: depends on platform/OF match data for many MediaTek SoCs, clk framework including exclusive rate locks, MMIO, PWM waveform callbacks, and PWM core.

Risks and test signals: clock enable reference counting is subtle because write paths temporarily enable clocks and may add an extra enable for active outputs. Test bootloader-enabled channels, SoC-specific register bases/widths, PWM4/5 fixup on MT7623/MT7628, 26 MHz selector clearing, max 1 GHz rate validation, waveform round-trip accuracy, and remove/unbind clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-meson.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-meson.c

Purpose: drives Amlogic Meson PWM blocks, which combine per-channel mux/divider/gate clock controls with high/low counters in two output registers. It supports legacy clock-name bindings, v2 index-based bindings, and S4-style externally provided clocks.

Important APIs/types/functions: `struct meson_pwm` stores SoC data, two `meson_pwm_channel` instances, MMIO base, and a spinlock protecting shared `REG_MISC_AB`. `meson_pwm_calc()`, `meson_pwm_enable()`, `meson_pwm_disable()`, `meson_pwm_apply()`, and `meson_pwm_get_state()` implement PWM ops. Channel initialization is split into `meson_pwm_init_clocks_meson8b_*()` and `meson_pwm_init_channels_s4()`.

Control flow: probe maps registers, initializes the spinlock, selects SoC data, initializes per-channel clocks, and registers two PWMs. Request enables the selected channel clock. Apply records polarity, handles disabled inverted output specially on old hardware without polarity support, or computes clock rate/high/low counts, sets clock rate, writes count and enable/constant/invert bits under the spinlock. Get-state reads the shared misc and channel count registers and derives period/duty from channel clock rate.

State and persistence: per-channel software caches desired rate, high/low counts, constant-output flag, and inverted flag; hardware registers store active counts and enable bits. Legacy hardware cannot accurately read back emulated inverted polarity, which is documented in the source comments.

Dependencies and integration: depends on platform/OF, clk provider APIs for registering mux/divider/gate clocks, raw OF clock gets for S4, spinlocks, MMIO, and PWM core. Many compatible strings select parent names and feature flags.

Risks and test signals: polarity behavior differs by hardware generation, and older emulation intentionally makes get-state imperfect. Shared `REG_MISC_AB` updates must stay locked against clock framework operations. Test legacy and v2 bindings, S4 clock cleanup, constant 0/100% duty, inverted disabled state, clock-rate rounding, and concurrent two-channel updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-meson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-microchip-core.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-microchip-core.c

Purpose: implements the Microchip FPGA corePWM block, with a shared prescale/period and per-channel positive/negative edge registers for up to sixteen PWM outputs.

Important APIs/types/functions: `struct mchp_core_pwm_chip` stores MMIO base, clock, mutex, channel count, and shared period parameters. `mchp_core_pwm_calc_period()`, `mchp_core_pwm_calc_duty()`, `mchp_core_pwm_apply_duty()`, `mchp_core_pwm_apply_locked()`, `mchp_core_pwm_get_state()`, and `mchp_core_pwm_wait_for_sync_update()` handle rounding and hardware programming.

Control flow: probe maps registers, gets the clock, reads or configures channel count from OF match data, initializes the mutex, and registers the PWM chip. Apply locks the shared state, computes feasible shared prescale/period steps, rejects period changes that conflict with active users, writes shared registers and per-channel edge registers, requests synchronous update, waits for sync completion, and toggles channel enable. Get-state decodes shared period and channel edges.

State and persistence: shared period/prescale are hardware-global and mirrored in driver state for conflict checking. Per-channel duty/enable are in MMIO registers. No persistent state exists outside hardware; no explicit suspend/resume code is present.

Dependencies and integration: depends on platform/OF, clk, mutexes, MMIO, PWM core, and Microchip corePWM register semantics.

Risks and test signals: shared-period constraints and sync-update timeouts are main risks. Test multiple active channels, period conflict rejection, 0%/100% duty edge programming, sync timeout, channel-count match data, and get-state after hardware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-microchip-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mtk-disp.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mtk-disp.c

Purpose: provides MediaTek display backlight PWM support. The hardware is a single display PWM with display-specific clocking, optional commit register behavior, and high-width/period fields suited to panel brightness control.

Important APIs/types/functions: `struct mtk_disp_pwm` stores base address, main/MM clocks, SoC data, and enabled state. `struct mtk_pwm_data` describes register offsets and whether the SoC has commit bits or blended clock behavior. `mtk_disp_pwm_apply()`, `mtk_disp_pwm_get_state()`, and `mtk_disp_pwm_update_bits()` implement behavior.

Control flow: probe maps registers, gets clocks, stores SoC data, and registers one PWM. Apply rejects unsupported polarity, enables clocks before programming, computes clock divider and high/period fields, writes display PWM registers and optional commit bits, toggles enable, and disables clocks if the output is off. Get-state enables clocks as needed, reads divider/period/high fields, and reconstructs period/duty.

State and persistence: hardware registers hold PWM configuration. The driver tracks whether clocks/output are currently enabled to avoid unnecessary clock toggles. No system PM restore is implemented in this file.

Dependencies and integration: depends on platform/OF, clk framework, MMIO, PWM core, and MediaTek display subsystem clock topology.

Risks and test signals: display backlight users are sensitive to glitches during duty updates and clock gating. Test all SoC data variants, commit behavior, enable/disable clock balance, divider limits, 0% duty, get-state when disabled, and panel brightness ramping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mtk-disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mxs.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mxs.c

Purpose: drives Freescale MXS PWM hardware with per-channel active/period registers and a small clock divider table.

Important APIs/types/functions: `struct mxs_pwm_chip` stores MMIO base and clock. `mxs_pwm_apply()` computes period count, duty count, divider selection from `cdiv_shift[]`, active/inactive polarity bits, and enable control. Probe reads the `fsl,pwm-number` property and registers that many channels.

Control flow: probe maps registers, gets/enables the clock, determines channel count, and registers the PWM chip. Apply rejects periods that cannot fit the divider/count encoding, writes active count and period/polarity/divider fields, then sets or clears the channel enable bit through SET/CLR aliases.

State and persistence: hardware registers hold all state; the driver keeps no channel cache. Clock is enabled for the lifetime of the device after probe. No get-state or PM callbacks are present.

Dependencies and integration: depends on OF/platform, clk, MMIO set/clear aliases, device property `fsl,pwm-number`, and PWM core.

Risks and test signals: channel count comes from firmware data, so bad DT can expose nonexistent channels. Test divider selection boundaries, normal/inverse polarity bits, enable set/clear aliases, requested period beyond 16-bit range, and clock disable cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mxs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ntxec.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-ntxec.c

Purpose: exposes the Netronix embedded controller backlight/PWM interface as a one-channel PWM provider using EC register writes.

Important APIs/types/functions: `struct ntxec_pwm` stores the parent `ntxec` device. `ntxec_pwm_set_raw_period_and_duty_cycle()` writes period and duty low/high bytes. `ntxec_pwm_apply()` validates normal polarity and period limit, converts nanoseconds to 125 ns ticks, writes raw period/duty, and toggles the enable register. Probe allocates and registers one PWM.

Control flow: apply rejects inverted polarity and periods above 16-bit tick range, disables immediately when requested, otherwise writes period/duty registers and enables the output. Duty is clamped to the requested period before conversion.

State and persistence: the EC owns actual register state. The driver keeps no cache and has no get-state or PM restore; EC reset/power behavior must be handled by reapplying consumer state.

Dependencies and integration: depends on the Netronix EC parent driver, EC register access helper, platform device creation, and PWM core.

Risks and test signals: EC communication failures can leave partial period/duty state if multi-register writes fail mid-sequence. Test max period (`125 ns * 0xffff`), 0/100% duty, disable behavior, parent EC reset, and register-write error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ntxec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-omap-dmtimer.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-omap-dmtimer.c

Purpose: implements PWM output using an OMAP dual-mode timer instance, turning timer load/match/toggle behavior into a one-channel PWM provider.

Important APIs/types/functions: `struct pwm_omap_dmtimer_chip` holds the PWM chip, timer pointer, mutex, clock rate, and timer ops. `pwm_omap_dmtimer_config()`, `pwm_omap_dmtimer_set_polarity()`, `pwm_omap_dmtimer_apply()`, `pwm_omap_dmtimer_start()`, `pwm_omap_dmtimer_is_enabled()`, and `pwm_omap_dmtimer_polarity()` implement behavior around dmtimer callbacks.

Control flow: probe requests a timer by phandle or platform data, gets timer ops and functional clock rate, configures PWM capability, and registers one PWM. Apply locks, programs load and match values for requested period/duty, configures output trigger mode and polarity, starts/stops the timer according to enabled state, and preserves timer state rules needed by OMAP hardware.

State and persistence: timer hardware holds counter, load, match, trigger, and enable state. The driver stores timer handle and clock rate but no persistent waveform cache. Remove unregisters the PWM and releases/stops the timer.

Dependencies and integration: depends on OMAP dmtimer platform APIs, clock rate from timer fclk, mutexes, platform/OF, and PWM core. It is an integration layer over another kernel timer driver rather than direct MMIO.

Risks and test signals: timer ownership conflicts and dmtimer callback semantics are the main risks. Test phandle lookup, unavailable timers, polarity changes, load minimum values, long/short periods, remove while enabled, and timer clock-rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-omap-dmtimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pca9685.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-pca9685.c

Purpose: implements PWM support for the NXP PCA9685 I2C 16-channel, 12-bit PWM/LED controller, exposing 16 per-channel PWMs plus an all-channels pseudo-channel.

Important APIs/types/functions: `struct pca9685` stores regmap, mutex, prescale, and active-channel bitmap. `pca9685_round_waveform_tohw/fromhw()`, `pca9685_read_waveform()`, `pca9685_write_waveform()`, `pca9685_pwm_request()`, `pca9685_pwm_free()`, and sleep-mode helpers implement the PWM waveform API. Regmap callbacks define readable/writeable/volatile registers.

Control flow: probe creates an I2C regmap, resets MODE registers, selects output driver behavior, reads or programs prescale, enables runtime PM, and registers 17 PWM entries. Request marks a channel active and prevents unsafe prescaler changes. Waveform write may change global prescale only when no other active channel conflicts, enters sleep for prescale programming, then writes four LED registers or all-channel registers. Free clears active tracking and can allow sleep/prescale changes.

State and persistence: hardware registers store mode, prescale, and on/off counts. Software tracks active channels and cached prescale to enforce global-frequency constraints. Runtime suspend enters chip sleep mode; resume leaves sleep.

Dependencies and integration: depends on I2C, regmap, runtime PM, mutexes, OF/ACPI/I2C IDs, PWM waveform API, and optional all-channel semantics encoded as channel index 16.

Risks and test signals: prescale is global, so changing one channel can disturb others unless correctly blocked. Test multi-channel period conflicts, all-channel pseudo-PWM behavior, sleep/resume, full-on/full-off LED bits, regmap errors, and request/free active bitmap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pca9685.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-pxa.c

Purpose: provides PWM support for Intel/Marvell PXA and compatible PWM blocks, including platform-ID and OF variants with one or two channels depending on device data.

Important APIs/types/functions: `struct pxa_pwm_chip` stores clock, MMIO base, and selected channel offset. `pxa_pwm_config()` computes prescaler, period count, and duty count, then writes `PWMCR`, `PWMDCR`, and `PWMPCR`. `pxa_pwm_apply()` manages enable/disable and normal polarity. Probe selects channel/resource based on platform data, ID flags, or OF compatible.

Control flow: probe resolves whether the device exposes a secondary PWM, maps the proper MMIO resource, gets the clock, sets ops, and registers one PWM instance. Apply rejects inverted polarity, disables output when requested, or enables the clock, configures registers, and sets the enable bit.

State and persistence: runtime state is hardware register state and clock enable. The driver has no get-state, no software cache, and no suspend/resume handling.

Dependencies and integration: depends on platform device IDs, optional OF matching for `marvell,pxa250-pwm` and `marvell,pxa270-pwm`, clk framework, MMIO, and PWM core.

Risks and test signals: channel/resource selection varies by platform ID and can map the wrong resource if board data is inconsistent. Test primary and secondary PWM IDs, OF compatibles, prescaler/count limits, disable clock balance, polarity rejection, and legacy board-file probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pxa.c -->
