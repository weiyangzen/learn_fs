# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-lpcg-scu.c

## Purpose
Implements LPCG gate clocks used on SCU-based i.MX8 platforms. It controls LPCG software and hardware autogate bits and handles the e10858 write-synchronization erratum.

## Important APIs, Types, And Functions
`struct clk_lpcg_scu` stores `clk_hw`, register address, bit index, hardware-autogate flag, and saved state. `clk_lpcg_scu_enable()` and `clk_lpcg_scu_disable()` update the two-bit gate field under `imx_lpcg_scu_lock`. `lpcg_e10858_writel()` performs the write plus delay/readback required by the erratum. `__imx_clk_lpcg_scu()` registers a clock, and `imx_clk_lpcg_scu_unregister()` frees it. `imx_clk_lpcg_scu_pm_ops` saves/restores LPCG state in noirq suspend/resume.

## Control Flow
Enable clears the field and writes software-enable plus optional hardware-autogate selection. Disable clears the field. Both use the current clock rate to choose readback versus nanosecond delay. Registration allocates a clock object, sets `CLK_SET_RATE_PARENT`, registers it, and optionally stores it as device drvdata for PM.

## State And Persistence Behavior
Hardware state is the LPCG register. The driver saves one raw register value per device-backed LPCG for suspend and restores it on resume, skipping names beginning with `hdmi_lpcg`.

## Dependencies And Integration Points
Used by `clk-imx8qxp-lpcg.c` and declared in `clk-scu.h`. Depends on common clock framework, MMIO access, spinlocks, delay helpers, and system sleep PM callbacks.

## Risks
The erratum delay is rate-dependent; a wrong parent rate can under-delay low-frequency gates. Register fields are two bits wide and shifted by `bit_idx`; incorrect bit indexes affect adjacent gate fields. PM drvdata only tracks one clock per device, so multi-output DT paths must be reviewed with this limitation.

## Test Signals
Enable/disable LPCG-backed UART/I2C/USDHC/ENET clocks, verify e10858-safe writes on low-rate clocks, run suspend/resume, and check HDMI LPCG special-case behavior.
