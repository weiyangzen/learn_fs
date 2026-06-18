# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-legacy.c

## Purpose
`gpiolib-legacy.c` implements deprecated integer-GPIO request/free helpers and their devres wrapper. It preserves older kernel driver APIs while delegating to descriptor-based gpiolib internals.

## Important APIs, Types, And Functions
Exported functions are `gpio_free()`, `gpio_request_one()`, `gpio_request()`, and `devm_gpio_request_one()`. Internal `devm_gpio_release()` releases integer GPIOs through `gpio_free()`.

## Control Flow
`gpio_request()` translates an integer GPIO to a descriptor with `gpio_to_desc()` and returns `-EPROBE_DEFER` if no descriptor exists, preserving legacy compatibility for GPIOs that may appear later. `gpio_request_one()` requests the GPIO, configures it as input or output according to `GPIOF_*` flags, and frees it on configuration failure. `devm_gpio_request_one()` performs the same setup and installs a devres cleanup action.

## State And Persistence
Runtime state is descriptor request ownership and direction state in core gpiolib. Managed legacy requests persist until the device devres action runs or explicit cleanup occurs.

## Dependencies And Integration Points
The file depends on legacy `linux/gpio.h`, descriptor consumer and driver APIs, and devres. It bridges old integer-based callers to descriptor APIs such as `gpiod_request()`, `gpiod_free()`, and direction setters.

## Risks
The APIs are deprecated and less expressive than descriptor-based APIs. Integer GPIO lookup can obscure firmware mapping errors, and `-EPROBE_DEFER` for missing descriptors is compatibility behavior that may surprise new code.

## Test Signals
Build and runtime tests should cover valid and invalid integer GPIOs, input/output initial direction flags, failure cleanup, devm cleanup on detach, and probe deferral compatibility.
