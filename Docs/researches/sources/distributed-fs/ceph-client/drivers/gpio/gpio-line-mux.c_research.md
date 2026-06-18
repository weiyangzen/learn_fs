<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-line-mux.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-line-mux.c

## Purpose
`gpio-line-mux.c` creates an input-only virtual gpiochip where each virtual line selects a mux state and reads one shared physical GPIO.

## Important APIs, types, and functions
`struct gpio_lmux` embeds the gpiochip, a `mux_control`, the shared `muxed_gpio`, and the variable-length mux state table. `gpio_lmux_gpio_get()` selects the mux state with a 100 us delay, reads the raw GPIO value, and deselects the mux. Probe reads `gpio-line-mux-states`.

## Control flow
Probe counts `gpio-line-mux-states`, allocates enough storage for the state array, gets the mux controller and `muxed` GPIO input, reads the state array, initializes a can-sleep dynamic-base gpiochip, and registers it. Each get operation performs select/read/deselect serially through the mux framework.

## State and persistence behavior
The driver stores only the static state mapping. It does not cache input values and has no output state. Mux state is temporary and deselected after each read.

## Dependencies and integration points
It binds to `gpio-line-mux`, depends on the Linux mux consumer API and GPIO consumer API, and exposes firmware-node-backed virtual GPIO lines to other consumers.

## Risks and edge cases
If `gpiod_get_raw_value_cansleep()` fails or returns while mux deselect also fails, the deselect return value is ignored. Concurrent reads rely on mux framework serialization. Only input direction is supported.

## Test signals
Test invalid or empty mux-state property, mux select failure, raw input reads for each virtual offset, mux deselect calls, and consumers that require can-sleep GPIO access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-line-mux.c -->
