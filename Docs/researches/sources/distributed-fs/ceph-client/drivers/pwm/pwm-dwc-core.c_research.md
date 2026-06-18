# sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc-core.c

Purpose: provides the shared PWM core for Synopsys DesignWare timer/PWM controllers, used by bus-specific frontends such as the PCI driver.

Important APIs/types/functions: `__dwc_pwm_set_enable()` toggles timer enable. `__dwc_pwm_configure_timer()` converts duty and period into low/high load counts and programs PWM user mode. `dwc_pwm_apply()` requires inverted polarity and manages runtime PM around enabled state. `dwc_pwm_get_state()` reads load counts and control register. `dwc_pwm_alloc()` allocates an eight-channel PWM chip, sets `clk_ns = 10`, and exports the helper in namespace `dwc_pwm`.

Control flow: frontend drivers call `dwc_pwm_alloc()`, set `dwc->base`, and register the chip. Apply enables runtime PM when starting from disabled, programs timer registers by disabling, writing low/high load counts, setting mode/PWM bits, and conditionally enabling. Disable clears enable and drops runtime PM.

State and persistence: shared state is the MMIO base, fixed input clock period, and optional context stored by frontend code. Hardware timer registers hold active configuration.

Dependencies and integration: depends on the PWM core, runtime PM, exported namespace `dwc_pwm`, and register definitions in `pwm-dwc.h`.

Risks and test signals: hardware cannot represent 0 percent or 100 percent duty because both low and high counts must be at least one clock. Runtime PM get/put return values are not checked. Test signals include invalid normal polarity, min/max load counts, enable/disable PM balancing, get-state in PWM and non-PWM modes, and frontend allocation/register sequencing.
