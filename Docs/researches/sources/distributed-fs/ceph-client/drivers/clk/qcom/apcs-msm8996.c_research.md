# sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8996.c

## Purpose
`apcs-msm8996.c` provides the early MSM8996 `sys_apcs_aux` clock used while CPU cluster PLLs are initialized. It programs the APCS auxiliary divider and exposes the result as a fixed 300 MHz clock to simplify early CPU-clock bootstrapping.

## Important APIs, Types, And Functions
The driver uses `qcom_apcs_msm8996_clk_probe()`, `dev_get_regmap()`, `regmap_read()`, `regmap_update_bits()`, `udelay()`, `devm_clk_hw_register_fixed_rate()`, and `devm_of_clk_add_hw_provider()`. Register definitions cover `APCS_AUX_OFFSET`, `APCS_AUX_DIV_MASK`, and `APCS_AUX_DIV_2`.

## Control Flow, State, And Persistence
Probe obtains the parent regmap, reads the APCS auxiliary register, writes divider bits to divide by two, waits 5 microseconds for hardware stability, registers fixed-rate `sys_apcs_aux`, and publishes it as the OF clock provider. Driver registration uses `postcore_initcall()` so the provider is available early enough for CPU cluster clock setup. Runtime state is the hardware divider plus the fixed-rate clock registration.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the parent APCS regmap, early platform-driver registration, CCF fixed-rate clocks, and MSM8996 CPU cluster clock drivers that use the auxiliary source during PLL setup. Risks include declaring a fixed 300 MHz rate that must match the parent/divider reality, insufficient stabilization delay, register write failures not being checked, and early init ordering regressions that can break CPU bring-up. Test signals include early boot on MSM8996, CPU PLL setup success, `sys_apcs_aux` visible before dependent CPU clocks, no fw_devlink delay of CPU clock drivers, and stable secondary CPU bring-up.
