# sources/distributed-fs/ceph-client/drivers/pwm/pwm-xilinx.c

Purpose: exposes the Xilinx LogiCORE AXI Timer as a single PWM output when the device tree node declares PWM cells. It reuses timer register definitions from `clocksource/timer-xilinx.h` and models the two timer counters as period and duty generators.

Important APIs, types, and functions: `xilinx_timer_tlr_cycles()` maps a cycle count into the timer load register based on up/down counting. `xilinx_timer_get_period()` converts a hardware load register back to nanoseconds. `xilinx_timer_pwm_enabled()` validates the two timer control registers against the supported PWM mode. `xilinx_pwm_apply()` implements PWM configuration and enable/disable. `xilinx_pwm_get_state()` reconstructs PWM state from hardware. `xilinx_pwm_probe()` initializes regmap, clock, counter width, and the PWM chip.

Control flow: probe rejects nodes lacking `#pwm-cells` so timer-only bindings can be handled elsewhere, allocates a one-channel PWM chip, maps the register resource, creates a little-endian 32-bit regmap, requires `xlnx,one-timer-only` to be false, accepts counter widths 8/16/32, gets and locks `s_axi_aclk`, then registers the chip. Apply rejects inverted polarity, converts requested period and duty to cycles with overflow guards, clamps period to the representable `priv->max + 2`, rejects periods below two cycles, clamps duty, adjusts 100 percent duty down by one cycle, and maps sub-two-cycle duty to constant low behavior. It writes TLR0/TLR1 and either lets a running PWM reload naturally or initializes the counters with LOAD followed by ENALL. Disabled state clears both TCSR registers.

State and persistence: persistent state is entirely in timer registers and the exclusive clock rate. `get_state` reads TLR and TCSR registers and treats a configuration matching `TCSR_PWM_SET` as enabled. It maps equal period and duty back to zero duty because this hardware produces low output in that case.

Dependencies and integration: integrates with PWM core, platform/OF, regmap MMIO, clock framework, and the Xilinx timer register contract. It takes an exclusive clock-rate reference so timing math remains stable while registered.

Risks: documented limitations include possible one-cycle glitch when changing period and duty together, no true 100 percent duty, normal polarity only, and disabled output always low. The driver assumes active-high Generate Out signals but cannot validate that from device tree. Existing bootloader state is only considered supported if the TCSR bits exactly match this driver's PWM mode.

Test signals: verify probe rejects one-timer-only nodes, exercise min/max counter widths, compare requested and observed period/duty with clock-rate changes blocked, inspect `get_state` after bootloader-preconfigured PWM, and test disable always drives low.
