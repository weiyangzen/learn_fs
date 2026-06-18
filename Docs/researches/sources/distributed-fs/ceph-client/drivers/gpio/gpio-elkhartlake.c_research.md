
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-elkhartlake.c

Purpose: provides an auxiliary-bus wrapper that instantiates Intel Elkhart Lake PSE GPIO using the shared Tangier GPIO implementation.

Important APIs/types/functions: `ehl_gpio_probe()` consumes `struct ehl_pse_io_data`, allocates `struct tng_gpio`, fills register base, IRQ, GPIO info, and wake-register offsets, then calls `devm_tng_gpio_probe()`. It imports the `GPIO_TANGIER` namespace and reuses `tng_gpio_pm_ops`.

Control flow: auxiliary probe validates platform data, maps the memory resource carried by the auxiliary device, sets fixed `ngpio` to 30, assigns EHL-specific wake registers (`GWMR_EHL`, `GWSR_EHL`, `GSIR_EHL`), calls the common Tangier probe helper, and stores driver data on the auxiliary device.

State and persistence behavior: this file owns no independent GPIO state after handoff; Tangier common code owns GPIO, IRQ, and PM state. The wrapper persists only the initialized `struct tng_gpio` allocated with devm.

Dependencies and integration points: depends on the Intel PSE auxiliary device model, `linux/ehl_pse_io_aux.h`, `gpio-tangier.h`, and Tangier helper APIs. The auxiliary id is `EHL_PSE_IO_NAME "." EHL_PSE_GPIO_NAME`.

Risks: all behavior depends on platform data being populated by the parent PSE driver. Fixed line count and wake-register constants must match the hardware block. Errors in Tangier common code surface through this wrapper.

Test signals: auxiliary device binding, missing platform-data failure, MMIO mapping failure, Tangier probe success, 30-line gpiochip exposure, wake register behavior through shared PM ops, and namespace import/build checks.
