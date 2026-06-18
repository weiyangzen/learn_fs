<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-hlcdc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atmel-hlcdc.c

Purpose: implements the MFD core for Atmel/Microchip HLCDC/XLCDC display blocks. It creates a custom MMIO regmap with synchronization-aware writes, gathers shared clocks and IRQ, and registers PWM and display-controller children.

Important APIs and functions: `atmel_hlcdc_probe` initializes `struct atmel_hlcdc` and MFD cells. Custom regmap callbacks are `regmap_atmel_hlcdc_reg_write` and `regmap_atmel_hlcdc_reg_read`; writes to low control registers wait for `ATMEL_HLCDC_SIP` to clear before writing.

Control flow: probe maps registers, gets IRQ 0, obtains `periph_clk`, obtains either `sys_clk` or fallback `lvds_pll_clk`, obtains `slow_clk`, initializes the custom 32-bit stride regmap, stores shared state as driver data, and adds `"atmel-hlcdc-pwm"` and `"atmel-hlcdc-dc"` children.

State and persistence: shared state includes IRQ, clocks, and regmap in `struct atmel_hlcdc`. The custom regmap context stores MMIO base and device for error reporting. Hardware display/PWM state is managed by children.

Dependencies and integration points: depends on platform resources, clock framework, regmap custom callbacks, MFD core, and HLCDC register definitions from `linux/mfd/atmel-hlcdc.h`. Child display and PWM drivers use the shared regmap and clocks from parent driver data.

Risks: synchronization polling uses an atomic timeout of 100 microseconds for certain registers; slow hardware or wrong clocking can produce write failures. The clock selection fallback requires one of `sys_clk` or `lvds_pll_clk`; firmware names must match. Child resource creation has no explicit IRQ domain, so children rely on parent state rather than MFD resources for interrupt access.

Test signals: probe on each OF compatible, clock-resource combinations for RGB/MIPI and LVDS systems, regmap write timeout behavior while SIP is set, PWM and display child binding, display modeset tests, and XLCDC-compatible build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-hlcdc.c -->
