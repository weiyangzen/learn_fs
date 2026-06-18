<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-imx-scu.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-imx-scu.c

## Purpose
`gpio-imx-scu.c` exposes NXP i.MX SCU board resources as output-only GPIOs controlled through the System Controller Unit firmware API.

## Important APIs, types, and functions
`struct scu_gpio_priv` holds a gpiochip, mutex, device pointer, and SCU IPC handle. `scu_rsrc_arr` maps GPIO offsets to `IMX_SC_R_BOARD_R0..R7`. Operations are `imx_scu_gpio_get()`, `imx_scu_gpio_set()`, `imx_scu_gpio_get_direction()`, and `imx_scu_gpio_probe()`.

## Control flow
The driver registers at `subsys_initcall_sync` so board control lines are available early. Probe obtains the SCU handle, initializes a mutex, fills an eight-line dynamic-base gpiochip, and registers it. Get and set serialize calls to `imx_sc_misc_get_control()` and `imx_sc_misc_set_control()`.

## State and persistence behavior
State lives in SCU firmware and the hardware resources it controls. The kernel stores no output cache; get queries firmware every time. The driver always reports output direction and has no input-direction transition.

## Dependencies and integration points
It binds to `fsl,imx8qxp-sc-gpio`, depends on i.MX SCU RM/misc firmware APIs and DT resource constants, and integrates with consumers that need SCU-controlled board pins.

## Risks and edge cases
SCU IPC failures are returned directly and logged. The offset-to-resource map is fixed at eight entries, so firmware must not expose a different line count. Direction is hard-coded output even though `get()` can read current level.

## Test signals
Probe on i.MX8QXP SCU systems, get/set firmware success and error injection, concurrency under multiple consumers, and validation that all eight board resources map to expected physical pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-imx-scu.c -->
