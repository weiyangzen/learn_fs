# subset-b-005171 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-raspberrypi-poe.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-raspberrypi-poe.c

## Purpose

`pwm-raspberrypi-poe.c` exposes the Raspberry Pi firmware-controlled PoE HAT fan PWM as a Linux PWM chip. It is not a memory-mapped timer driver; it talks to the Raspberry Pi firmware mailbox using `RPI_FIRMWARE_GET_POE_HAT_VAL` and `RPI_FIRMWARE_SET_POE_HAT_VAL`. The hardware surface is intentionally narrow: one firmware PWM block with a fixed 12.5 kHz period, 8-bit duty register, normal polarity only, and no real disable bit.

## Important APIs, types, and functions

The private `struct raspberrypi_pwm` stores the firmware handle and a cached `duty_cycle` in the firmware's 0..255 scale. `struct raspberrypi_pwm_prop` is the packed little-endian mailbox payload containing register, value, and return status. `raspberrypi_pwm_set_property()` and `raspberrypi_pwm_get_property()` wrap firmware calls and translate firmware-side nonzero `ret` into `-EIO`. `raspberrypi_pwm_get_state()` reports the fixed period and converts the cached register value into nanoseconds. `raspberrypi_pwm_apply()` validates polarity and period, maps disabled to duty 0, rounds duty down to the 8-bit firmware scale, and updates firmware only when the cached value changes. Probe obtains the parent firmware node, gets the firmware handle, allocates a PWM chip with `RASPBERRYPI_FIRMWARE_PWM_NUM` channels, reads the initial duty register, and registers with `devm_pwmchip_add()`.

## Control flow

A consumer call enters `.apply`; invalid inverted polarity or too-short period returns `-EINVAL`. Enabled states are quantized to the firmware range; disabled states are simulated by writing duty 0. The write goes through the firmware property channel, and only on success is the software cache updated. `.get_state` never asks firmware again after probe, so runtime reads reflect driver-owned cached state rather than an external firmware reconfiguration.

## State and persistence behavior

The only software state is the cached duty value. Actual persistence is in the firmware-controlled PoE HAT register. Because there is no hardware disable bit, `enabled` is derived from nonzero duty. Firmware/hardware changes outside this driver can make `get_state()` stale until reprobe.

## Dependencies and integration points

The driver depends on the PWM framework, OF platform matching for `raspberrypi,firmware-poe-pwm`, Raspberry Pi firmware APIs, and the DT binding channel count. It integrates with the firmware node by walking to the parent OF node and defers probe if firmware is not ready.

## Risks and edge cases

Duty and period are heavily constrained; consumers requesting arbitrary periods will be accepted only if the requested period is at least 80 us but the actual period remains fixed. Duty quantization can round small nonzero duty requests to 0, effectively disabling output. There is no locking around cached duty, relying on the PWM core's normal serialization. Firmware errors are surfaced but leave the cache unchanged.

## Test signals

Build with Raspberry Pi firmware PWM support, bind through DT, and verify probe reads the initial duty. Runtime tests should apply disabled, minimum nonzero, half, and full duty states, reject inverted polarity, and confirm firmware writes occur only when the quantized duty changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-raspberrypi-poe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rcar.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rcar.c

## Purpose

`pwm-rcar.c` is the Renesas R-Car PWM Timer driver. It presents a single PWM output backed by two memory-mapped registers, `RCAR_PWMCR` for enable, sync, and clock control, and `RCAR_PWMCNT` for cycle and phase counters. The hardware cannot produce 0% duty, and the driver supports only normal polarity.

## Important APIs, types, and functions

`struct rcar_pwm_chip` stores the mapped base and functional clock. `rcar_pwm_get_clock_division()` chooses a clock division up to `RCAR_PWM_MAX_DIVISION` so the 10-bit cycle counter can represent the requested period. `rcar_pwm_set_clock_control()` encodes the odd/even divider split into `CCMD` and `CC0`. `rcar_pwm_set_counter()` computes 10-bit cycle and phase values using `mul_u64_u64_div_u64()` and rejects zero cycle or zero phase to avoid prohibited hardware settings. `rcar_pwm_request()` and `rcar_pwm_free()` bracket channel use with runtime PM. `rcar_pwm_apply()` validates polarity, disables on disabled state, sets sync, programs counters and clock control, clears sync, then enables.

## Control flow

Probe maps MMIO, gets the clock, enables runtime PM, and registers one PWM. Consumers must request the PWM before applying states, causing runtime PM to keep the block active. Apply disables immediately for disabled states. For enabled states, division is calculated first; if the requested period is outside range, no registers are updated. Otherwise the driver sets `SYNC`, writes `PWMCNT`, updates clock control, clears `SYNC`, and sets `EN0`.

## State and persistence behavior

There is no software shadow of period or duty. Hardware register state persists until rewritten or reset. Runtime PM is used at request/free granularity rather than each apply, so mapped register access assumes the PWM has been requested and the device is active.

## Dependencies and integration points

The driver depends on platform resources, `devm_platform_ioremap_resource()`, a clock, runtime PM, and the PWM core. It binds to `renesas,pwm-rcar` and uses classic `pwmchip_add()`/`pwmchip_remove()` rather than fully managed registration.

## Risks and edge cases

0% duty is rejected because `PH0` cannot be zero; consumers expecting a disabled-equivalent enabled 0% signal will get `-EINVAL`. Very long periods can exceed the divider/counter range and return `-ERANGE`. `pm_runtime_get_sync()` errors in `.request` are returned directly, but the code does not balance a failed get with `pm_runtime_put_noidle()`, a pattern worth checking against current PM expectations. No `.get_state` exists, so initial hardware state is not reported.

## Test signals

Test normal-polarity period/duty combinations across divider boundaries, rejection of inverted polarity and 0% duty, disable clearing `EN0`, and enable refusal if either counter field is zero. Hardware tests should verify `SYNC` bracketing and period accuracy from the clock/divider math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rcar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-renesas-tpu.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-renesas-tpu.c

## Purpose

`pwm-renesas-tpu.c` drives the Renesas Timer Pulse Unit in PWM mode for R-Mobile/R-Car style TPU blocks. It exposes four PWM channels, each with its own TPU channel register window plus a shared timer start register. The driver supports both PWM polarities by programming timer output actions and handles 0%/100% duty as static pin levels to avoid unnecessary timer operation.

## Important APIs, types, and functions

`struct tpu_device` owns the platform device, lock, MMIO base, clock, and four `struct tpu_pwm_device` channel states. Each channel caches `timer_on`, channel number, polarity, prescaler, period, and duty. `tpu_pwm_set_pin()` selects inactive, PWM, or active output via `TIOR`. `tpu_pwm_start_stop()` serializes updates to shared `TSTR`. `tpu_pwm_timer_start()` powers/clocks the block, stops and reconfigures the channel, writes `TCR`, `TMDR`, `TIOR`, `TGRA`, and `TGRB`, then starts counting. `tpu_pwm_config()` computes a 16-bit period with prescaler values 1, 4, 16, and 64, supports duty-only updates, and converts 0%/100% into fixed pin states. `.apply` coordinates polarity changes, disable, config, and enable.

## Control flow

Probe maps the TPU register block, gets the clock, enables runtime PM, and registers four PWM devices. A request initializes per-channel software state. Apply first handles polarity changes by disabling any active PWM before changing `tpd->polarity`. Enabled updates call `tpu_pwm_config()`, which may either update only `TGRA` while running or perform a full stop/reconfigure/start. Enabling a previously disabled channel calls `tpu_pwm_timer_start()`. Disable briefly starts the timer if needed so pin output configuration can be changed, drives inactive, then stops and releases clock/PM.

## State and persistence behavior

The driver keeps substantial per-channel shadow state because no `.get_state` is implemented and the hardware registers are programmed from cached values. `timer_on` tracks clock/runtime-PM ownership. The shared `TSTR` is protected by a spinlock. Register state persists in hardware while powered, but cached `period`, `duty`, `prescaler`, and `polarity` are the driver's source of truth.

## Dependencies and integration points

It depends on MMIO, a clock, runtime PM, the PWM core, and OF compatibles `renesas,tpu-r8a73a4`, `renesas,tpu-r8a7740`, `renesas,tpu-r8a7790`, and `renesas,tpu`. The shared `TSTR` register means the channel instances are not independent at the register-write level.

## Risks and edge cases

The clock rate is rejected if above 1 GHz to avoid overflow; periods outside 16-bit range after max prescale return `-EINVAL`. 0% and 100% duty disable the timer and force static levels, which can surprise consumers expecting `enabled=true` to imply a running counter. `tpu_pwm_timer_start()` calls `pm_runtime_get_sync()` but does not check its return before enabling the clock. Disable ignores a possible error from `tpu_pwm_timer_start()`. There is no `get_state`, so bootloader state is not visible.

## Test signals

Exercise all four channels, polarity changes while enabled, duty-only updates, full period changes, 0% and 100% fixed-level paths, runtime PM clock balancing, and shared `TSTR` updates under concurrent channel activity. Static review should verify all `pm_runtime_get_sync()` paths are properly balanced on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-renesas-tpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rockchip.c

## Purpose

`pwm-rockchip.c` supports several Rockchip PWM register layouts and feature sets through a per-compatible `struct rockchip_pwm_data`. It exposes one PWM per device instance, with layout variants for early RK2928, RK3288-style, VOP PWM, and RK3328-style locked updates.

## Important APIs, types, and functions

`struct rockchip_pwm_chip` stores functional and APB clocks, mapped registers, and variant data. `struct rockchip_pwm_regs` describes duty, period, counter, and control offsets. `rockchip_pwm_get_state()` enables both clocks, reads period/duty/control, converts ticks using the variant prescaler, and reports polarity when supported. `rockchip_pwm_config()` computes 32-bit period/duty ticks, optionally locks updates with `PWM_LOCK_EN`, writes duty and period, updates polarity bits, and unlocks. `rockchip_pwm_enable()` handles the functional clock reference and sets or clears the variant enable bit pattern. `rockchip_pwm_apply()` enables clocks, reads current state, disables first for polarity changes on non-locking hardware, configures, then toggles enable if needed.

## Control flow

Probe maps MMIO, obtains the PWM clock and optional separate APB clock, prepares/enables both, determines whether hardware is already enabled, registers the PWM chip, and leaves the PWM clock enabled only if the PWM was already running. Apply always enables the APB and functional clocks for register access, calls `pwm_get_state()` to obtain current logical state, stages configuration, then disables the extra references before returning.

## State and persistence behavior

No separate software period/duty state is maintained; `get_state()` reads hardware. Clock references are used as state: enabled PWM outputs keep the functional clock enabled, while the APB clock is temporary for accesses. Hardware register contents persist across apply calls and may be inherited from boot.

## Dependencies and integration points

The driver depends on the clock framework, OF matching via `device_get_match_data()`, MMIO resources, and the PWM core. It supports both legacy unnamed clocks and named `pwm`/`pclk` configurations. Variant data controls register offsets, prescaler, polarity support, lock support, and enable masks.

## Risks and edge cases

`rockchip_pwm_get_state()` enables `pclk`, then if enabling `clk` fails it returns without disabling `pclk`, which looks like a clock leak on that error path. If `clk_enable(pc->clk)` fails in `.apply` after `pclk` was enabled, `pclk` is likewise not disabled. Non-locking hardware must be disabled for live polarity changes, causing a visible output gap. Tick values saturate to `U32_MAX` rather than rejecting overlarge requests, so actual periods can differ from requested extremes.

## Test signals

Test each compatible layout, boot-enabled clock preservation, separate and shared APB clock DT cases, polarity changes on locked and non-locked variants, saturated period/duty requests, and failure-injection for clock enables to catch leaked references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rz-mtu3.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rz-mtu3.c

## Purpose

`pwm-rz-mtu3.c` exposes PWM outputs from the Renesas RZ/G2L MTU3a multi-function timer. Seven hardware MTU channels are mapped into twelve logical PWM outputs because most hardware channels have two I/O outputs while MTU1 and MTU2 have one. The driver currently supports normal polarity only and drives outputs to Hi-Z on disable.

## Important APIs, types, and functions

`struct rz_mtu3_pwm_chip` stores the parent MTU clock, cached rate, a mutex, per-hardware-channel request and enable counts, current prescaler, and channel mapping. `channel_map[]` maps logical PWM numbers to MTU channels and I/O count. `rz_mtu3_get_channel()` resolves a logical PWM to its parent MTU channel. `rz_mtu3_pwm_request()`/`free()` claim and release shared MTU channels via the MFD parent. `rz_mtu3_pwm_config()` computes cycles, chooses prescale values 1/4/16/64, enforces shared-prescaler constraints, writes `TCR` and `TGR[A-D]`, and handles temporary runtime PM for disabled outputs. `get_state()` reads `TCR` and TGR registers when output is enabled. Runtime PM callbacks gate the shared clock.

## Control flow

Probe retrieves the parent `struct rz_mtu3`, skips unsupported MTU5 and MTU8, attaches child channel data, takes an exclusive clock-rate reference, validates rate, enables runtime PM, and registers twelve PWMs. Request increments a per-hardware-channel user count and only claims the parent channel for the first user. Apply rejects inverted polarity, disables if requested, otherwise locks the chip, configures shared timer registers, and enables the output if it was previously disabled.

## State and persistence behavior

Software state tracks shared-channel ownership and active users. `enable_count[ch]` controls when the parent counter is actually enabled/disabled, and `prescale[ch]` caches the shared prescaler. Hardware register state persists while powered; runtime PM suspends the clock when no enabled channels need it. `get_state()` reports useful values only when the channel output is enabled.

## Dependencies and integration points

This is an MFD child of the RZ MTU3 driver and depends on `linux/mfd/rz-mtu3.h` helpers such as `rz_mtu3_request_channel()`, `rz_mtu3_enable()`, and 8/16-bit channel accessors. It also depends on runtime PM and the PWM core.

## Risks and edge cases

Two logical outputs sharing a hardware MTU channel cannot freely choose different prescalers. If multiple outputs are enabled and a new request would require a lower prescale than the cached one, config returns `-EBUSY`; otherwise it may reuse a larger prescale with less resolution. The code decrements `enable_count` on disable without an explicit underflow guard, relying on PWM core state. Disabled output is Hi-Z, not forced inactive. Only normal polarity is accepted despite hardware support.

## Test signals

Test all logical-to-hardware channel mappings, especially single-output MTU1/2 and dual-output channels. Exercise sibling outputs with equal and conflicting periods, `-EBUSY` paths, runtime PM transitions, `get_state()` while enabled and disabled, and request/free behavior when two logical outputs share one MTU channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rz-mtu3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rzg2l-gpt.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rzg2l-gpt.c

## Purpose

`pwm-rzg2l-gpt.c` drives the Renesas RZ/G2L General PWM Timer. It maps eight hardware GPT counters into sixteen logical PWM outputs, two per counter. The counter, period, mode, and prescaler are shared by sibling outputs; each subchannel has its own compare register and output-enable bits. The driver supports normal polarity only.

## Important APIs, types, and functions

`struct rzg2l_gpt_chip` stores MMIO, a mutex, a kHz clock rate, cached period ticks, and request/enable counts per hardware channel. `RZG2L_GET_CH()`, `rzg2l_gpt_subchannel()`, and `rzg2l_gpt_sibling()` map logical PWM numbers. `rzg2l_gpt_calculate_prescale()` chooses hardware prescale up to 1024. `rzg2l_gpt_config()` caps period to `RZG2L_MAX_TICKS`, enforces sibling shared-period constraints, programs saw-wave up-counting mode, prescaler, period, compare, counter reset, and buffer disable. `rzg2l_gpt_enable()`/`disable()` manipulate output bits and shared counter start. `get_state()` reconstructs period and duty from `GTCR`, `GTPR`, and `GTCCR`.

## Control flow

Probe maps registers, deasserts reset, enables the clock, locks clock rate exclusively, validates a nonzero integer-kHz rate not above 1 GHz, initializes the mutex, and registers sixteen PWMs. Request and free only update per-channel request counts. Apply holds the mutex, rejects inverted polarity, disables requested outputs by clearing their output-enable bit and possibly stopping the shared counter, or configures and enables active outputs.

## State and persistence behavior

The driver caches `period_ticks[ch]` to enforce shared counter requirements. Request count indicates whether both siblings are in use; enable count controls whether the counter should continue running. Hardware state is fully in MMIO and remains while powered because the driver uses a permanently enabled managed clock rather than runtime PM.

## Dependencies and integration points

The driver depends on OF compatible `renesas,rzg2l-gpt`, MMIO, reset controls, clock framework exclusive-rate APIs, and the PWM core. It uses `guard(mutex)` scoped locking and standard bitfield helpers.

## Risks and edge cases

Sibling outputs cannot currently run different periods. If a sibling is enabled and a second output requests a shorter period than the cached period, config returns `-EBUSY`; longer requests are coerced to the existing period. The source comment notes a limitation that disabling one channel may stop the other, but the implementation uses enable counts to stop only when the last output disables; hardware behavior should be verified. Duty and period are rounded down to ticks, and disabled outputs are driven inactive. Normal-only polarity limits hardware capability.

## Test signals

Validate all sixteen outputs, sibling period sharing, compare register selection for A/B outputs, disable of one active sibling while the other remains active, `get_state()` conversions, reset/clock probe paths, and rejection of non-kHz or greater-than-1GHz clock rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-rzg2l-gpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-samsung.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-samsung.c

## Purpose

`pwm-samsung.c` supports Samsung S3C/S5P/Exynos timer PWM blocks. It exposes up to `SAMSUNG_PWM_NUM` channels, but only channels declared as outputs by variant data or DT are requestable. The block is shared with the Samsung clocksource driver, so register access uses a shared spinlock when necessary.

## Important APIs, types, and functions

`struct samsung_pwm_channel` caches period, duty, and input tick time for resume and reconfiguration. `struct samsung_pwm_chip` stores variant data, inverter and disabled masks, clocks, MMIO base, and channel caches. `to_tcon_channel()` handles the TCON register's channel gap. `pwm_samsung_calc_tin()` selects either external TCLK or divided base clock and writes `TCFG1`. `__pwm_samsung_config()` calculates down-counter `TCNTB` and `TCMPB`, handles the missing 0% duty by forcing at least one tick, writes registers, and manually updates after 100% duty transitions. `pwm_samsung_set_polarity()` accounts for inverted hardware semantics. Resume restores cached configuration and enable/disable state.

## Control flow

Probe obtains variant data from OF or platform data, maps registers, enables the base timer clock, initializes supported outputs to normal logical polarity, obtains optional external clocks, and registers the chip. Request rejects channels without output pins and clears channel cache. Apply disables before polarity changes, rejects periods above one second, configures the timer, and enables if previously disabled. Enable toggles manual update, start, and autoreload bits under the shared lock. Disable clears autoreload and handles 100% duty with manual update to avoid stuck-high output.

## State and persistence behavior

The driver maintains software cache for period/duty/tick rate, inverter state, and disabled state. These are needed for system resume because hardware registers may be lost. Hardware register state includes TCFG0/TCFG1 dividers, TCON control bits, TCNTB/TCMPB counters, and optional external clock selection.

## Dependencies and integration points

It integrates with `<clocksource/samsung_pwm.h>` for variant definitions and possibly a shared `samsung_pwm_lock`. Device tree uses compatibles such as `samsung,s3c2410-pwm` and optional `samsung,pwm-outputs`. Clock dependencies are `timers`, optional `pwm-tclk0`, and optional `pwm-tclk1`.

## Risks and edge cases

The hardware counter semantics invert normal expectations: inverted hardware means normal logical polarity. 0% duty cannot be represented and is approximated. Only periods up to one second are accepted to avoid 64-bit arithmetic. Shared registers and possible clocksource users make locking important. DT output masks must be correct; otherwise request fails. Resume depends on cached state and requested flags, so unrequested boot-configured PWMs are not restored by this driver.

## Test signals

Test each variant's counter width, TCON channel mapping including channel 4 autoreload bit, `samsung,pwm-outputs` validation, polarity toggles, 0% and 100% duty behavior, external TCLK fallback, and resume after configured enabled and disabled states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-samsung.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sifive.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sifive.c

## Purpose

`pwm-sifive.c` drives the SiFive PWM IP block with four compare outputs sharing one counter and one scale-derived period. The hardware compare register represents inactive time and cannot generate a true 0% duty cycle; the driver inverts compare values so consumers see a conventional active-high PWM model.

## Important APIs, types, and functions

`struct pwm_sifive_ddata` stores the parent device, mutex, clock notifier, prepared clock, MMIO base, real and requested approximate periods, and user count. `pwm_sifive_update_clock()` programs `PWMCFG` with `EN_ALWAYS` and a scale value chosen from the requested period and clock rate, then computes the real period. `pwm_sifive_get_state()` reads `PWMCMP`, converts inactive counts to duty, checks `EN_ALWAYS`, and reports normal polarity. `pwm_sifive_apply()` computes an inverted compare value, enforces shared-period ownership, updates period/scale under lock, enables the clock if needed, writes compare, and disables the clock for disabled states. A clock notifier recomputes period on post-rate-change events.

## Control flow

Probe allocates four PWMs, maps registers, gets a prepared clock, enables it to inspect existing state, counts already enabled outputs by reading `PWMCFG` and `PWMCMP`, adjusts clock references so each active PWM owns one enable, registers a clock notifier, registers the PWM chip, and stores drvdata. Request/free update `user_count`. Apply allows a period change only for the sole user or initial setup, then writes the compare register. Remove unregisters the notifier and disables clocks for PWMs still marked enabled.

## State and persistence behavior

The hardware period is shared by all outputs; `approx_period` is the requested logical period and `real_period` is the actual quantized period after scale selection. `user_count` protects against one consumer changing period underneath another. Clock enable references mirror active PWM count. Hardware register state persists, but driver software state is authoritative for period reporting after probe.

## Dependencies and integration points

The driver depends on the clock framework including notifiers, MMIO, OF compatible `sifive,pwm0`, and the PWM core. It uses `devm_clk_get_prepared()` but manages enable counts manually.

## Risks and edge cases

All four outputs share period, so conflicting users get `-EBUSY`. There is an unavoidable mixed-setting window when period and duty change together. Hardware cannot generate 0% duty; disabled maps to duty 0 and clock disable, but compare quantization still has limits. If clock rate changes, all outputs' actual periods shift and the notifier rewrites scale. The enabled-PWM detection in probe treats `PWMCMP > 0` as enabled even though compare is inactive time, which should be validated against the intended semantics.

## Test signals

Test shared-period conflict handling, clock-rate notifier behavior, boot-enabled PWM clock reference reconstruction, duty inversion at 0/near-full/full duty, remove-time clock balancing, and `.get_state()` consistency with hardware compare values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sifive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sl28cpld.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sl28cpld.c

## Purpose

`pwm-sl28cpld.c` exposes a single PWM implemented inside the Kontron sl28 CPLD. The core uses a 32 kHz 8-bit counter with four selectable reset points, so changing frequency also changes available duty resolution. There is no public datasheet; the driver documents the timing model in comments.

## Important APIs, types, and functions

`struct sl28cpld_pwm` stores the parent regmap and register offset. Macros convert prescaler to period and cycle count to duty nanoseconds. `sl28cpld_pwm_get_state()` reads `CTRL` and `CYCLE`, extracts enable and prescaler, computes period and duty, and clamps invalid bootloader combinations to sane PWM-core values. `sl28cpld_pwm_apply()` rejects inverted polarity, chooses the smallest prescaler whose period is not above the request, computes cycle count, works around the prescaler-0 100% limitation by using prescaler 1, and orders `CYCLE` and `CTRL` writes to avoid invalid transient combinations when shortening periods.

## Control flow

Probe requires a parent device, obtains its regmap, reads the `reg` property as an offset, allocates one PWM, and registers it. Apply computes the complete next state in software, then performs one or two regmap writes depending on whether duty must be written before control. Disable is simply `CTRL` without the enable bit.

## State and persistence behavior

No driver shadow state exists. Hardware state persists in CPLD registers and is fully read by `.get_state()`. Because regmap writes are not atomic across control and duty registers, transient states are possible.

## Dependencies and integration points

The driver depends on a parent MFD/regmap provider and OF compatible `kontron,sl28cpld-pwm`. The `reg` property selects the PWM block offset within the CPLD.

## Risks and edge cases

Prescaler changes can glitch because the counter is not reset and prescaler/cycle cannot be written atomically. 100% duty with prescaler 0 is remapped to prescaler 1, preserving logical all-on output at a different nominal frequency. Write failures between the two registers can leave inconsistent hardware. `order_base_2()` period selection can reject periods below the maximum-frequency mode with `-ERANGE`.

## Test signals

Test all four prescaler modes, 100% duty workaround, period-shortening and period-lengthening write order, invalid bootloader register combinations in `.get_state()`, regmap error propagation, and disabled output behavior on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sl28cpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sophgo-sg2042.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sophgo-sg2042.c

## Purpose

`pwm-sophgo-sg2042.c` supports Sophgo SG2042 and SG2044 PWM controllers. Both variants have four channels with `PERIOD` and `HLPERIOD` registers; SG2044 adds polarity, output-enable, and start registers. SG2042 supports only normal polarity and treats period/high-period zero as stopped output pulled high.

## Important APIs, types, and functions

`struct sg2042_pwm_ddata` stores MMIO base and fixed APB clock rate. `struct sg2042_chip_data` embeds the variant-specific `pwm_ops`. `pwm_sg2042_set_dutycycle()` converts nanoseconds to clock ticks and writes period/high-period. `pwm_sg2042_apply()` rejects inverted polarity and disables by writing zeros. `pwm_sg2042_get_state()` reads period/high-period, reports disabled when period is zero, clamps high time to period, and reports normal polarity. SG2044 helpers update `PWMSTART`, output enable, and polarity bits; `pwm_sg2044_apply()` programs polarity/duty, toggles start to refresh, and enables output only for enabled states.

## Control flow

Probe matches variant data, maps registers, enables the `apb` clock, takes an exclusive clock-rate reference, validates nonzero rate not above 1 GHz, optionally deasserts shared reset, sets variant ops, marks the chip atomic, and registers four PWMs. Apply is direct MMIO programming with no sleeping clock gates after probe.

## State and persistence behavior

No software shadow state is kept. Register values persist in hardware. The clock rate is fixed via exclusive rate locking and cached for conversions. SG2044 state includes separate polarity, output-direction, and start bits, while SG2042 enable state is inferred from nonzero period.

## Dependencies and integration points

The driver binds to `sophgo,sg2042-pwm` and `sophgo,sg2044-pwm`, depends on MMIO, an enabled `apb` clock, optional shared reset, exclusive clock-rate APIs, and the PWM core. `chip->atomic = true` signals that operations do not sleep after setup.

## Risks and edge cases

SG2042 `get_state()` always reports normal polarity even for SG2044, so SG2044 inverted state is not reconstructed from hardware. SG2044 `.apply()` writes period/high-period even for disabled states, then clears start; SG2042 disabled writes zeros. Tick conversion truncates and saturates to `U32_MAX`, so actual long periods can be capped. There is no locking around read-modify-write SG2044 shared registers, relying on PWM core serialization.

## Test signals

Test both compatibles, normal and inverted SG2044 polarity, disabled semantics, period zero reads, high-period greater than period clamping, clock-rate validation, and concurrent-looking updates to shared SG2044 control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sophgo-sg2042.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-spear.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-spear.c

## Purpose

`pwm-spear.c` drives the ST SPEAr PWM controller with four channels. Each channel has a control register, duty-cycle register, and period register at 16-byte strides. SPEAr1340 additionally requires a master PWM enable bit.

## Important APIs, types, and functions

`struct spear_pwm_chip` stores MMIO base and prepared clock. `spear_pwm_config()` searches prescale values until 16-bit period and duty counts fit, rejecting unrepresentable periods and zero duty/period counts. It temporarily enables the clock, writes prescale, duty, and period, then disables the clock. `spear_pwm_enable()` enables the clock and sets `PWMCR_PWM_ENABLE`, leaving the clock on while active. `spear_pwm_disable()` clears the enable bit and disables the clock. `.apply` supports normal polarity only.

## Control flow

Probe maps registers, gets a prepared clock, sets `chip->ops`, and for `st,spear1340-pwm` temporarily enables the clock to set `PWMMCR_PWM_ENABLE`. Apply disables active channels when requested, otherwise configures timing and enables if the channel was previously disabled.

## State and persistence behavior

No software state is kept; channel enable state is managed through PWM core state and the hardware control bit. Active channels hold a clock enable reference; configuration of inactive channels borrows the clock briefly. Hardware registers persist while powered.

## Dependencies and integration points

The driver binds to `st,spear320-pwm` and `st,spear1340-pwm`, uses MMIO resources, a clock, and the PWM core. It uses old-style `pwm_ops` with only `.apply`, so no hardware state readback is available.

## Risks and edge cases

The config path rejects zero duty because `PWMDCR_MIN_DUTY` is 1, so an enabled 0% duty request fails instead of producing a constant inactive level. The prescaler loop can be expensive in worst case but bounded by 14-bit prescaler range. There is no locking around shared master control, though only probe touches it. No `.get_state` means bootloader settings are invisible.

## Test signals

Test all four channels, SPEAr1340 master enable, min and max period/duty counts, rejection of inverted polarity and 0% duty, clock reference balance across configure/enable/disable, and period accuracy over prescaler transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-spear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sprd.c

## Purpose

`pwm-sprd.c` supports Spreadtrum/Unisoc PWM blocks such as UMS512. It exposes up to four channels, each with its own register bank and two clocks: an enable clock and a PWM output clock. The driver fixes the modulus register to its maximum value and selects prescale to approximate the requested period.

## Important APIs, types, and functions

`struct sprd_pwm_chn` stores per-channel bulk clocks and output clock rate. `struct sprd_pwm_chip` stores MMIO base and channel descriptors. `sprd_pwm_clk_init()` discovers available channel clocks by name pairs (`enableN`, `pwmN`) and returns the number of usable channels. `sprd_pwm_get_state()` enables channel clocks for reading, reports enable bit, reconstructs period from prescale and fixed `SPRD_PWM_MOD_MAX`, reconstructs duty from the duty register, and leaves clocks enabled if the channel is active. `sprd_pwm_config()` writes prescale, modulus, and duty, deliberately writing duty last because it triggers hardware application. `.apply` gates clocks around enable/disable and supports normal polarity only.

## Control flow

Probe discovers clocks before allocating the PWM chip, maps registers, copies channel metadata, and registers `npwm` equal to discovered channels. Apply enables clocks before configuring an inactive channel, writes timing registers, then sets enable. Disable clears enable immediately and disables clocks.

## State and persistence behavior

No explicit software shadow of period/duty exists. Channel clock enable state is tied to active PWM state; `get_state()` keeps clocks enabled when it discovers an already enabled channel to synchronize clock references with hardware. Hardware applies new period/duty only when duty is written.

## Dependencies and integration points

The driver binds to `sprd,ums512-pwm`, depends on per-channel named clocks, MMIO resources, and the PWM core. It can expose fewer than four PWMs if clock discovery stops at a missing `-ENOENT` channel.

## Risks and edge cases

`sprd_pwm_config()` computes duty using integer arithmetic with `int duty_ns`/`period_ns` parameters and can lose precision. Prescale is clamped to 8 bits, so long requested periods saturate. Disable does not wait for the current period to complete. If `sprd_pwm_get_state()` fails enabling the second clock, bulk enable unwinding is handled by the clock core, but failure paths should be tested. A missing clock for an early channel stops discovery of later channels.

## Test signals

Test clock discovery with one to four channels, get-state on boot-enabled channels, duty-last application, prescale saturation, immediate disable behavior, inverted polarity rejection, and clock reference balance after get_state/apply sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sti.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sti.c

## Purpose

`pwm-sti.c` drives STMicroelectronics STi PWM/capture hardware. The IP has a common PWM output enable and shared period prescaler across configured PWM outputs, plus optional capture inputs with interrupt-driven edge sampling.

## Important APIs, types, and functions

`struct sti_pwm_chip` stores clocks, regmap/regmap fields, channel counts, capture data, configured-output bitmask, enable count, and MMIO. `sti_pwm_get_prescale()` accepts only periods exactly representable by the fixed counter and prescaler model. `sti_pwm_config()` enforces shared-period compatibility across configured PWM outputs, writes prescaler fields and duty registers, and disables capture interrupts. `sti_pwm_enable()`/`disable()` manage common output enable and clock references through `en_count`. `sti_pwm_capture()` programs capture edge detection, enables capture, waits for interrupt snapshots, and converts captured ticks to period/duty. `sti_pwm_interrupt()` alternates capture edges, stores three timestamps, disables capture when complete, and acknowledges interrupts.

## Control flow

Probe reads `st,pwm-num-chan` and `st,capture-num-chan`, maps MMIO through regmap, requests an IRQ, initializes regmap fields, gets clocks only for configured PWM/capture roles, initializes capture wait queues, and registers the chip. Apply validates channel range and normal polarity, disables if requested, otherwise configures and enables. Capture serializes per input with a mutex and waits up to the caller timeout.

## State and persistence behavior

`configured` tracks which PWM outputs have programmed state; `cur` remembers the reference channel for shared period comparison. `en_count` tracks the common output-enable gate. Capture state is transient in per-channel `snapshot[]` and `index`. Hardware registers persist, but no `get_state` is provided for PWM outputs.

## Dependencies and integration points

The driver depends on OF properties for channel counts, MMIO regmap, IRQs, `pwm` and `capture` clocks, wait queues, and the PWM core's optional capture API. It uses regmap fields for split prescaler and enable/status bits.

## Risks and edge cases

PWM outputs share period, so a second output with a different period is rejected. `sti_pwm_config()` enables `pwm_clk`, then if enabling `cpt_clk` fails it returns without disabling `pwm_clk`, which looks like a clock leak. `sti_pwm_enable()` has a similar leak if enabling `cpt_clk` or writing enable fails after `pwm_clk` is enabled. Capture returns 0 period/duty for no or very low-frequency signals, and interrupt races or missed edges can affect snapshots. There is no PWM `.get_state`.

## Test signals

Test shared-period acceptance/rejection, exact-prescaler period validation, common enable count with multiple outputs, capture of known duty waveforms, timeout/no-signal capture, IRQ acknowledgement, and clock-failure injection for cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32-lp.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32-lp.c

## Purpose

`pwm-stm32-lp.c` drives PWM output from STM32 low-power timers. Some LPTIMER instances have a single PWM output controlled by `CMP`/`ARR` and `WAVPOL`; others have dedicated capture/compare channels, each exposed as a PWM output with polarity and enable in `CCMR1`.

## Important APIs, types, and functions

`struct stm32_pwm_lp` stores the parent LPTIMER clock, regmap, and number of compare channels. `stm32_pwm_lp_update_allowed()` determines whether shared enable, prescaler, and reload values can be changed when multiple compare channels exist. `stm32_pwm_lp_compare_channel_apply()` updates CC enable/polarity and handles the required delay when changing polarity on an enabled channel. `stm32_pwm_lp_apply()` computes prescaler and ARR/CMP values, enforces shared ARR/prescaler constraints, enables/disables the LPTIMER and clock, polls write-complete flags, and starts continuous mode. `get_state()` reads CR, CFGR, ARR, CMP/CCR, and CCMR1 as applicable.

## Control flow

Probe obtains the parent `struct stm32_lptimer`, chooses `npwm` as one or the number of CC channels, stores parent regmap/clock, and registers. Apply first handles disable by clearing CC output, zeroing compare, possibly disabling the LPTIMER, and disabling the clock. Enabled apply calculates the closest representable period, checks shared-resource constraints, enables the clock if needed, updates CFGR if prescaler or single-output polarity changes, enables the timer for register writes, writes ARR and CMP/CCR, polls for write completion, enables the compare channel, and starts counting if reenabled.

## State and persistence behavior

No separate software cache is kept; state is read from parent LPTIMER registers. Clock enable references are synchronized in `get_state()` for already enabled hardware. Shared prescaler and ARR are hardware-global for multiple CC channels.

## Dependencies and integration points

This is an MFD child of `stm32-lptimer`, using parent regmap and clock. It depends on LPTIMER register definitions, pinctrl PM state selection, and the PWM core. System suspend refuses to proceed if any PWM remains enabled.

## Risks and edge cases

Multiple CC outputs cannot independently change prescaler or ARR; conflicting enabled configurations return `-EBUSY`. Duty computation writes `prd - (1 + dty)`, so boundary behavior for 0% and 100% duty should be tested against hardware semantics. If an error occurs after enabling the clock for an inactive PWM, the error path disables it, but only for originally disabled channels. Suspend requires consumers to stop PWM first.

## Test signals

Test single-output and multi-CC instances, polarity changes on enabled channels and required delay, shared ARR/prescaler conflicts, write-complete polling timeout, boot-enabled get_state clock sync, suspend refusal with active PWM, and 0%/100% duty boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32-lp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32.c

## Purpose

`pwm-stm32.c` drives STM32 general-purpose/advanced timers through the newer PWM waveform API and optional DMA-backed capture. It supports up to four PWM outputs, complementary outputs when available, break inputs, shared timer period/prescaler constraints, and capture using paired input channels.

## Important APIs, types, and functions

`struct stm32_pwm` stores a mutex, parent timer clock/regmap, max ARR, complementary-output flag, breakinput configuration, and a DMA-aligned capture buffer. The waveform path uses `struct stm32_pwm_waveform` containing CCER, PSC, ARR, and CCR. `stm32_pwm_round_waveform_tohw()` converts requested waveform period/duty/offset to hardware values, honoring existing active-channel PSC/ARR. `stm32_pwm_write_waveform()` programs PSC/ARR, polarity, CCR, output mode, main output enable, CCER, update generation, and controller enable/disable. `read_waveform` and `round_waveform_fromhw` reconstruct logical waveform state. Capture uses `stm32_pwm_capture()` plus `stm32_pwm_raw_capture()` to configure PWM input mode and use timer DMA burst reads for rising/falling timestamps. Probe detects channel count and complementary output, configures break inputs, locks clock rate, and initializes clock references for already enabled channels.

## Control flow

Probe gets the parent `stm32_timers` MFD data, detects enabled channels and channel count by hardware registers or HWCFGR, allocates a PWM chip, validates regmap/clock, applies optional `st,breakinput`, detects complementary support, takes exclusive clock-rate control, checks the 1 GHz arithmetic limit, enables the clock once per already active output, and registers waveform ops. Waveform writes enable the clock for register access, reject conflicting PSC/ARR if other channels are active, configure output mode and polarity, enable the controller if transitioning active, or clear CCER/CEN and drop a clock reference when disabling.

## State and persistence behavior

The driver mostly uses hardware registers as state. Software state includes breakinput configuration and complementary capability. Active PWM outputs hold clock enable references. The shared timer PSC and ARR are global across channels, so active channels constrain later waveform writes.

## Dependencies and integration points

This is a child of `stm32-timers` and depends on its regmap, clock, max ARR, DMA helper `stm32_timers_dma_burst_read()` when `CONFIG_DMA_ENGINE` is enabled, pinctrl PM states, OF breakinput properties, and the PWM waveform/capture APIs.

## Risks and edge cases

Shared PSC/ARR means active channels cannot use arbitrary independent periods. `stm32_pwm_write_waveform()` enables the clock at entry and, when enabling a previously disabled channel, enables it a second time to create the active reference before the common exit disable; that refcount pattern is subtle and needs regression coverage. Capture requires no active PWM channels and at least two capture units for duty measurement. Input prescaler correction handles races, but DMA timing races are still documented in code. Suspend rejects active channels.

## Test signals

Test waveform conversion round trips, active-channel period conflicts, complementary outputs, 0%/100% and offset waveforms, breakinput validation/restoration, DMA capture across low and high frequencies, clock refcounts across enable/disable, and suspend/resume with inactive and active channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-stm32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-stmpe.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-stmpe.c

## Purpose

`pwm-stmpe.c` drives PWM outputs on STMPE2401 and STMPE2403 MFD expanders. It exposes three PWM channels implemented by writing small instruction programs into STMPE PWM instruction registers. STMPE1601 is explicitly rejected as unsupported.

## Important APIs, types, and functions

`struct stmpe_pwm` stores the parent STMPE device and `last_duty`. `stmpe_24xx_pwm_enable()`/`disable()` update `STMPE24XX_PWMCS` bits. `stmpe_24xx_pwm_config()` disables if currently active, selects the PWM alternate function for the relevant pin, maps duty to an 8-bit value, builds different instruction sequences for STMPE2401 ramping or STMPE2403 direct `LOAD`, writes three 16-bit instructions as byte pairs, optionally re-enables, and sleeps 200 ms for the program to take effect. `.apply` supports normal polarity only.

## Control flow

Probe validates the STMPE part number, allocates three PWMs, enables the STMPE PWM block, registers the chip, and stores drvdata. Apply disables active PWM for reprogramming, writes the instruction program, then enables if requested. Remove unregisters and disables the STMPE PWM block; the driver uses `module_platform_driver_probe()`, so runtime unbind is not expected.

## State and persistence behavior

`last_duty` is a single cached byte shared across all channels, not per-channel. Hardware program memory and enable bits persist in the STMPE device. The code uses `pwm_is_enabled()` for live state and blocks for 200 ms after programming.

## Dependencies and integration points

The driver depends on the STMPE MFD API (`stmpe_reg_read/write`, `stmpe_set_altfunc`, `stmpe_enable/disable`) and the PWM core. Pin numbering differs for STMPE2401/2403, adding `STMPE_PWM_24XX_PINBASE` to route channels to pins 21-23.

## Risks and edge cases

The single `last_duty` field appears to conflate all three channels; changing one channel can affect ramp programming decisions for another. The 200 ms sleep makes apply slow. Reprogramming disables the PWM, creating output gaps. Period is effectively not programmable in a general way despite accepting period/duty input. No `.get_state` exists. I2C/register failures can leave a partially written instruction program.

## Test signals

Test STMPE2401 and STMPE2403 separately, all three channels, per-channel duty changes after another channel changes to expose `last_duty` coupling, 0%/100% handling, alternate-function setup, disable/re-enable sequencing, and partial write error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-stmpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sun4i.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sun4i.c

## Purpose

`pwm-sun4i.c` supports Allwinner sun4i-family PWM controllers with one or two channels and SoC-specific support for prescaler bypass or direct module-clock output. It handles legacy shared control registers where each channel's control bits are separated by a fixed offset.

## Important APIs, types, and functions

`struct sun4i_pwm_data` describes whether the variant has prescaler bypass, direct mod-clock output, and how many PWMs exist. `sun4i_pwm_get_state()` reads control and period registers, handles direct-bypass mode specially, reconstructs polarity, enable, period, and duty. `sun4i_pwm_calculate()` chooses direct bypass for near-source-clock requests when supported, otherwise chooses a prescaler and period/duty counts. `sun4i_pwm_apply()` enables the module clock if needed, calculates parameters, updates bypass/prescaler/period/duty/polarity/enable bits, waits one current period before final disable, and gates the clock.

## Control flow

Probe gets variant data, maps MMIO, obtains `mod` or unnamed source clock plus optional `bus` clock and reset, deasserts reset, keeps the bus clock enabled for register access, and registers the chip. Apply reads current state, prepares the clock for inactive channels, computes new settings, handles direct-bypass early, writes period and control, and on disable waits for a full old period before clearing enable and clock-gating bits.

## State and persistence behavior

No software shadow state is kept. Hardware control and period registers are read for state. The bus clock remains enabled for the device lifetime, while the mod clock is enabled only for active outputs or temporary configuration. Reset is asserted on remove.

## Dependencies and integration points

The driver binds many Allwinner compatibles from A10 through H6. It depends on clocks, optional reset, MMIO, OF match data, and the PWM core. It relies on `pwm_get_state()` at apply time to decide clock and disable-delay behavior.

## Risks and edge cases

Direct clock bypass ignores normal PWM enable semantics and does not guarantee current-period completion. The expression `state->period * clk_rate` can overflow 64-bit in bypass detection for extreme values because both operands are not explicitly widened before multiplication. Shared control-register read/modify/write has no driver lock, relying on PWM core serialization. Disable sleeps for the previous period, which can be long. Some prescaler table entries are invalid zeros and must be skipped.

## Test signals

Test each variant data path, prescaler bypass, direct mod-clock output, polarity, long-period disable delay, reset and bus clock handling, boot-state readback, and extreme period values around bypass and prescaler boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sun4i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sunplus.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-sunplus.c

## Purpose

`pwm-sunplus.c` drives the Sunplus SP7021 PWM block with four channels. Each channel has frequency and duty registers, while enable, bypass, and counter-enable bits are shared in mode registers. The hardware supports normal polarity only, outputs low when disabled, and applies new frequency/duty immediately rather than at period boundaries.

## Important APIs, types, and functions

`struct sunplus_pwm` stores MMIO base and clock. `sunplus_pwm_apply()` rejects polarity changes, disables by clearing PWM output and counter-enable bits, calculates `dd_freq` from clock and requested period, writes the frequency register, computes an 8-bit duty value with channel select bits, handles 100% duty through bypass/high output, then writes duty and mode registers. `sunplus_pwm_get_state()` reads enable, frequency, and duty, reconstructs period/duty, and reports normal polarity. Probe enables the clock for the device lifetime and registers four PWMs.

## Control flow

Probe maps MMIO, gets and prepares/enables the clock, installs a managed action to disable it, and registers. Apply for enabled states writes FREQ before DUTY, then enables the counter and output. Disable immediately clears mode bits. No per-apply clock gating is used.

## State and persistence behavior

There is no software state; hardware registers are the source of truth. The clock remains prepared/enabled after probe. Mode registers persist until changed or reset.

## Dependencies and integration points

The driver binds `sunplus,sp7021-pwm`, depends on an unnamed clock, MMIO resources, managed cleanup, and the PWM core.

## Risks and edge cases

The code intentionally rejects any polarity different from the current PWM core state rather than accepting explicit normal polarity if current state is not initialized as normal. Frequency and duty writes are not atomic, so a short interval can run new frequency with old duty. Disable is immediate and does not finish the current period. Long periods saturate `dd_freq` to 16 bits, changing the actual period.

## Test signals

Test normal apply, 100% bypass, disable low output, frequency saturation, period/duty readback, rejection of inverted polarity, and visual/glitch behavior during live frequency/duty changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-sunplus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-tegra.c

## Purpose

`pwm-tegra.c` drives NVIDIA Tegra PWM controllers. Tegra20-style devices expose four channels sharing one controller clock, while Tegra186/Tegra194-style instances expose one channel and can change the clock rate dynamically through OPP. The register packs enable, 8-bit duty, and 13-bit frequency scale.

## Important APIs, types, and functions

`struct tegra_pwm_soc` describes channel count and maximum IP frequency. `struct tegra_pwm_chip` stores clock, reset, cached clock rate, minimum period, registers, and SoC data. `tegra_pwm_config()` computes 8-bit duty with rounded division, enforces the minimum period, optionally sets an OPP clock rate for single-channel variants, computes scale, uses runtime PM for register access if disabled, and writes the channel register. `tegra_pwm_enable()`/`disable()` set `PWM_ENABLE` and manage runtime PM. Runtime PM callbacks gate the clock and select pinctrl states.

## Control flow

Probe gets match data, maps registers, obtains clock, initializes the Tegra OPP table, enables runtime PM and resumes the device, sets maximum clock frequency, reads the actual clock rate, computes minimum period, deasserts reset, registers the chip, then runtime-suspends. Apply rejects inverted polarity, disables active channels when requested, configures enabled states, and enables if previously disabled.

## State and persistence behavior

`clk_rate` and `min_period_ns` are cached from the configured clock. Active outputs hold runtime PM references, which keep the clock prepared/enabled. Register state persists while powered; reset is asserted on remove. There is no `.get_state`.

## Dependencies and integration points

The driver depends on Tegra common OPP initialization, `dev_pm_opp_set_rate()`, runtime PM, pinctrl PM states, reset controls, clocks, and OF compatibles `nvidia,tegra20-pwm`, `nvidia,tegra186-pwm`, and `nvidia,tegra194-pwm`.

## Risks and edge cases

Reconfiguration while running is abrupt and does not wait for period completion. Duty beyond the 8-bit range is not explicitly clamped before shifting; invalid high duty can affect bits outside the duty field if the PWM core supplies duty greater than period. Single-channel clock-rate changes affect the whole controller instance and depend on OPP availability. Probe error paths force runtime suspend after partial setup and should be tested. No hardware readback is implemented.

## Test signals

Test each SoC data variant, minimum-period rejection, OPP rate selection for single-channel devices, runtime PM and pinctrl transitions, reset handling, disable inactive level, and live reconfiguration glitch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiecap.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiecap.c

## Purpose

`pwm-tiecap.c` drives Texas Instruments eCAP modules in APWM mode. It exposes one PWM channel per eCAP instance, using CAP1/CAP2 for inactive updates and CAP3/CAP4 shadow registers for live updates. On disable the PWM pin becomes input, so external wiring determines final level.

## Important APIs, types, and functions

`struct ecap_pwm_chip` stores clock rate, MMIO base, and suspend context. `ecap_pwm_config()` converts period/duty to cycles, enables runtime PM for register access, sets APWM mode and sync disabled, writes active or shadow registers depending on whether running, and clears APWM mode for inactive configuration. `ecap_pwm_set_polarity()` toggles `ECCTL2_APWM_POL_LOW`. `ecap_pwm_enable()` keeps runtime PM active and sets free-run/APWM mode. `ecap_pwm_disable()` clears free-run/APWM and releases runtime PM. Suspend/resume save and restore CAP3/CAP4/ECCTL2 and adjust runtime PM if the PWM was enabled.

## Control flow

Probe obtains `fck` from the device or legacy parent binding, reads clock rate, maps registers, registers one PWM, stores drvdata, and enables runtime PM. Apply handles polarity changes by disabling first, rejects periods above one second, configures timing, and enables if needed.

## State and persistence behavior

The driver keeps a suspend context for key registers. Active PWM state holds a runtime PM reference. Hardware shadow registers allow live period completion on reconfiguration. No `.get_state` exists.

## Dependencies and integration points

The driver binds `ti,am3352-ecap` and legacy `ti,am33xx-ecap`, uses runtime PM, an `fck` clock, MMIO, and the PWM core. It has compatibility code for obsolete parent-clock bindings.

## Risks and edge cases

`pm_runtime_get_sync()` return values are not checked in config, polarity, or save-context paths. Period and duty conversions truncate into 32-bit cycles and periods over one second are rejected. Disabled pin behavior is input/floating rather than a guaranteed inactive drive. No `.get_state` limits boot-state visibility.

## Test signals

Test normal and inverted polarity, live reconfiguration using shadow registers, disable pin behavior, suspend/resume with enabled and disabled PWM, legacy clock binding, runtime PM failure injection, and one-second period boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiecap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiehrpwm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiehrpwm.c

## Purpose

`pwm-tiehrpwm.c` drives Texas Instruments EHRPWM modules with two outputs sharing one time-base period. It programs the time-base, compare A/B, and action-qualifier registers, supports normal and inverted polarity, and saves/restores context for suspend.

## Important APIs, types, and functions

`struct ehrpwm_pwm_chip` stores clock rate, MMIO base, per-output requested period cycles, TBCLK, and saved context. `set_prescale_div()` searches time-base prescaler encodings. `ehrpwm_pwm_config()` enforces equal period across both outputs, computes period/duty cycles, chooses prescaler, programs TBCTL/TBPRD/CMPA/CMPB/AQCTL, and handles duty greater than period as constant output by suppressing compare action. `ehrpwm_pwm_enable()` disables software force and enables TBCLK. `ehrpwm_pwm_disable()` forces output low immediately and disables TBCLK/runtime PM. `.free` clears period ownership for a channel. Suspend/resume save and restore key registers and runtime PM references for active outputs.

## Control flow

Probe gets `fck`, reads rate, maps registers, gets and prepares `tbclk`, registers two PWMs, and enables runtime PM. Apply uses a scoped runtime-PM active guard, disables first for polarity changes, disables on requested inactive state, otherwise configures and enables if previously inactive.

## State and persistence behavior

`period_cycles[]` records each output's requested period to enforce the shared `TBPRD` constraint. Active outputs hold runtime PM and TBCLK enables. Context storage preserves time-base, compare, and action-qualifier registers across suspend.

## Dependencies and integration points

The driver binds `ti,am3352-ehrpwm` and `ti,am33xx-ehrpwm`, depends on `fck`, `tbclk`, runtime PM, MMIO, and the PWM core. It includes a likely legacy-binding check for `ti,am33xx-ecap` while probing EHRPWM clocks.

## Risks and edge cases

Both outputs must use the same period; conflicts return `-EINVAL` until the other channel is freed. The obsolete-binding compatibility check appears to test `ti,am33xx-ecap` in the EHRPWM driver, likely a copy/paste typo. Runtime PM guard plus explicit enable/disable refcounts are subtle and need balancing tests. Periods above one second are rejected, and no `.get_state` is available.

## Test signals

Test two-channel same-period operation, conflicting period rejection and `.free` reset, normal/inverted polarity, 100% duty handling, TBCLK enable/disable balance, suspend/resume register restore, and legacy clock-binding paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-tiehrpwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl-led.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl-led.c

## Purpose

`pwm-twl-led.c` exposes TWL4030 and TWL6030 LED PWM outputs through the PWM framework. It is specifically for LED terminals, not the generic TWL PWM outputs. TWL4030 provides two LED PWM outputs, while TWL6030 provides one LEDPWM output.

## Important APIs, types, and functions

TWL4030 paths use LED module registers `LEDEN` and `PWMA/PWMB`; `twl4030_pwmled_config()` maps relative duty to on/off-cycle values with the hardware's nonzero on-cycle limitation, while enable/disable toggles LED on/PWM bits. TWL6030 paths use `LED_PWM_CTRL1/2`; config writes an 8-bit on time, enable sets LED mode on, disable sets LED mode off. `twl6030_pwmled_request()` forces software-off mode, and `.free` restores hardware-controlled mode. Probe selects ops and channel count using `twl_class_is_4030()`.

## Control flow

Apply rejects unsupported polarity, returns early for disabled states after disabling active hardware, otherwise writes duty configuration and enables if previously disabled. TWL6030 request/free adjust mode ownership around consumer use. All hardware access is through TWL I2C helper functions.

## State and persistence behavior

No private state is allocated. State persists in TWL PMIC LED/PWM registers. The driver does not implement `.get_state`, and comments explicitly note it only implements relative duty cycle. TWL6030 request/free temporarily change LED mode away from hardware control.

## Dependencies and integration points

The driver depends on the TWL MFD I2C APIs, `twl_class_is_4030()`, OF compatibles `ti,twl4030-pwmled` and `ti,twl6030-pwmled`, and the PWM core. It does not manage clocks directly.

## Risks and edge cases

The hardware cannot represent true duty 0 in the configured PWM mode; comments say duty 0 produces one active tick and should preferably use disabled state. TWL4030's duty mapping wraps the maximum duty to off-cycle 1. TWL6030 `.apply` rejects polarity changes relative to current PWM core state, not specifically non-normal polarity. I2C failures can leave partial state. No readback means boot state is not synchronized.

## Test signals

Test TWL4030 two-output LED routing, TWL6030 request/free mode transitions, duty 0 and full duty mappings, disabled low/off behavior, I2C error propagation, and lack of `.get_state` behavior in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl-led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl.c

## Purpose

`pwm-twl.c` exposes the generic PWM outputs of TWL4030 and TWL6030 PMICs. TWL4030 has PWM0/PWM1 with pin muxing through interrupt bridge registers; TWL6030 has two PWM outputs controlled through `TOGGLE3`.

## Important APIs, types, and functions

`struct twl_pwm_chip` holds a mutex plus cached TWL6030 `TOGGLE3` state and TWL4030 pin-mux bits to restore on free. `twl_pwm_config()` writes the generic TWL PWM module on/off-cycle pair, with the same nonzero on-cycle mapping as TWL LED PWM. TWL4030 request/free save and restore GPIO6/GPIO7 mux fields in `PMBR1`; enable/disable sequence clock and enable bits in `GPBR1`. TWL6030 enable/disable use set/reset/toggle semantics in `TOGGLE3` and maintain the cached byte. Variant ops are selected at probe by `twl_class_is_4030()`.

## Control flow

Probe allocates two PWMs, initializes the mutex, chooses TWL4030 or TWL6030 ops, and registers. Apply rejects inverted polarity, disables active hardware when requested, otherwise writes duty configuration and enables if previously disabled. TWL4030 consumers get request/free mux management; TWL6030 does not implement request/free.

## State and persistence behavior

The driver caches only shared-control and mux information, not period/duty. Hardware state lives in TWL I2C registers. The mutex protects multi-step register sequences and cached bytes. No `.get_state` exists.

## Dependencies and integration points

It depends on TWL MFD I2C helpers and OF compatibles `ti,twl4030-pwm` and `ti,twl6030-pwm`. TWL4030 integration touches INTBR mux registers in addition to the PWM module.

## Risks and edge cases

TWL4030 mux restore is cached per bit mask but shared across channels; request/free ordering should be tested if both channels are used. The hardware cannot encode a true zero on-time in PWM mode. Multi-step TWL6030 disable writes can leave partial state on I2C failure. There is no state readback and no explicit period support beyond relative duty mapping.

## Test signals

Test TWL4030 mux save/restore for both channels, TWL6030 cached toggle state, duty mapping at 0/full, disable sequences, I2C failure paths, and consumer behavior without `.get_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-visconti.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-visconti.c

## Purpose

`pwm-visconti.c` drives Toshiba Visconti PWM hardware with four channels. The input clock is fixed at 1 MHz and can be divided by 1, 2, 4, or 8. Hardware shadows new values until `PCSR` is written, then switches after the current period completes; disabling also completes the current period and holds output low.

## Important APIs, types, and functions

`struct visconti_pwm_chip` stores MMIO base. `visconti_pwm_apply()` disables by writing zero period, otherwise caps period to the hardware maximum, clamps duty to period, converts nanoseconds to microsecond ticks, chooses the smallest power-of-two divider that fits the 16-bit period register, sets polarity in `PWMC`, writes duty to `PDUT`, and writes period to `PCSR` last to latch the shadowed settings. `visconti_pwm_get_state()` reads `PCSR`, `PDUT`, and `PWMC`, reconstructs period/duty/polarity, and currently reports enabled unconditionally.

## Control flow

Probe maps MMIO, allocates four PWMs, assigns ops, and registers. Apply is direct MMIO with no clocks or resets managed in this file. Enabled updates write control and duty before period to use hardware shadowing; disabled updates write period zero.

## State and persistence behavior

There is no software state. Hardware registers are source of truth. Shadowing ensures atomic transition on period boundary for active reconfiguration. The fixed 1 MHz timebase gives microsecond resolution.

## Dependencies and integration points

The driver binds to `toshiba,visconti-pwm`, depends on MMIO resources and the PWM core, and assumes any required clocking is handled outside this driver or by always-on hardware.

## Risks and edge cases

`get_state()` reports `enabled = true` even when `PCSR` is zero, so disabled hardware can be misreported with zero period. Periods above the hardware maximum are silently capped rather than rejected. Sub-microsecond periods become zero after division and return `-ERANGE`. The driver supports inverted polarity but only through the single active-level bit.

## Test signals

Test disable followed by get_state, maximum-period capping, sub-microsecond rejection, normal/inverted polarity, period-boundary atomic updates, and four-channel independent register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-visconti.c -->
