<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-jz4740.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-jz4740.c

Purpose: provides PWM support for Ingenic JZ4740/JZ4725B/X1000 TCU timer channels using the parent TCU regmap and per-channel timer clocks.

Important APIs/types/functions: `struct jz4740_pwm_chip` stores the TCU regmap and an array of per-channel clocks; `struct soc_info` supplies channel count. `jz4740_pwm_request()` enforces the `ingenic,pwm-channels-mask` property and gets `timerN` clocks. `jz4740_pwm_apply()` computes clock rate, period, duty, polarity/init level, and enables/stops the TCU channel.

Control flow: probe gets match data, allocates flexible clock storage, obtains the parent TCU regmap, and registers the PWM chip. Request gets and enables a timer clock. Apply rounds the clock rate down through `clk_round_rate()`, disables the channel, sets the new rate, resets the counter, writes duty and period registers, sets abrupt shutdown and initial level according to polarity/enabled state, then starts the counter if enabled. Free disables and releases the timer clock.

State and persistence: hardware TCU registers hold period, duty, counter, PWM mode, and enable state. The driver stores only per-request clock pointers. There is no get-state or PM restore in this file.

Dependencies and integration: depends on the Ingenic TCU MFD register map, syscon/regmap, named timer clocks, platform/OF matching, device properties on the parent, and PWM core.

Risks and test signals: the code assumes Ingenic clock `clk_round_rate()` rounds down, which is not guaranteed by the generic clk API. Channel mask handling can conflict with TCU users. Test masked channel rejection, all SoC channel counts, clock-rate rounding, full-duty clamp (`duty >= period`), polarity behavior, and apply while running because it does not wait for the current period to finish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-jz4740.c -->
