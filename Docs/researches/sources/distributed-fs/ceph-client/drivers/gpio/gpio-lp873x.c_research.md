<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp873x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp873x.c

## Purpose
`gpio-lp873x.c` exposes the two output-only GPO pins on TI LP873x PMICs.

## Important APIs, types, and functions
`struct lp873x_gpio` stores a gpiochip and parent LP873x pointer. GPIO callbacks include output-only direction reporting, `lp873x_gpio_request()` for GPO2 mux setup, get/set via `LP873X_REG_GPO_CTRL`, and `lp873x_gpio_set_config()` for open-drain/push-pull.

## Control flow
Probe copies a template chip, gets parent MFD data, sets the gpiochip parent, and registers it. Request for offset 1 changes `CLKIN_PIN_SEL` to route the pin to GPO2; offset 0 needs no muxing. Direction output and set update the value bit at `offset * 4`.

## State and persistence behavior
State is in PMIC regmap registers. The driver has no shadow and no input state. Both lines are always reported as outputs.

## Dependencies and integration points
It is a platform child named `lp873x-gpio`, depends on the LP873x MFD regmap, and exposes pinconf drive mode through gpiolib.

## Risks and edge cases
GPO2 request changes a shared pin mux and can affect clock input users. Direction input always fails. Register bit positions are spaced by four bits, so offset math must stay aligned with PMIC definitions.

## Test signals
Test request for offsets 0/1 and invalid offsets, GPO2 mux update, output get/set, open-drain/push-pull config, and PMIC regmap error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-lp873x.c -->
