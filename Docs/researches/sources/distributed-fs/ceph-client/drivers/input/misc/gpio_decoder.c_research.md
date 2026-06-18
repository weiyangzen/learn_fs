<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio_decoder.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/gpio_decoder.c

## Purpose
`gpio_decoder.c` reads multiple GPIO input lines as a binary-encoded value and reports changes on an absolute input axis. It is intended for simple hardware selectors or encoded position devices.

## Important APIs, Types, and Functions
`struct gpio_decoder` stores the GPIO array, device, target axis, and last stable value. `gpio_decoder_get_gpios_state()` reads up to 31 GPIOs with `gpiod_get_array_value_cansleep()` into a bitmap and returns the decoded integer with `bitmap_read()`. `gpio_decoder_poll_gpios()` is the input polling callback and emits `input_report_abs()` when the value changes.

## Control Flow
Probe reads optional `linux,axis`, acquires an unnamed GPIO array as inputs, validates at least two and no more than 31 lines, reads optional `decoder-max-value` or defaults to `2^ndescs - 1`, allocates input, sets ABS axis parameters, configures polling with `input_setup_polling()`, and registers input. Polling performs all runtime event generation.

## State and Persistence Behavior
Only `last_stable` is retained to suppress duplicate reports. The driver does not debounce or persist state.

## Dependencies and Integration Points
It binds via OF compatible `gpio-decoder`, uses firmware properties, GPIO descriptor arrays, input polling, and absolute-axis reporting.

## Risks and Test Signals
Risks include no explicit debounce despite the `last_stable` name, default axis value of zero if missing, GPIO ordering assumptions, and max-value mismatch with hardware encoding. Tests should cover GPIO count validation, custom axis and max value, transition reporting only on changes, read errors, and bitmap decoding order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio_decoder.c -->
