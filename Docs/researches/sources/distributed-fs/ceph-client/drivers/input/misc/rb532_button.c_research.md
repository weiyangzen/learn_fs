# sources/distributed-fs/ceph-client/drivers/input/misc/rb532_button.c

## Purpose
`rb532_button.c` polls the RouterBOARD 532 S1 button and reports it as `BTN_0`. It handles board-specific GPIO/UART alternate-function switching needed to read the shared GPIO pin.

## Important APIs, Types, and Functions
`struct rb532_button` holds the button GPIO descriptor. `rb532_button_pressed()` disables UART through `set_latch_u5()`, switches the pin to GPIO input, reads it, restores alternate function through `rb532_gpio_set_func(GPIO_BTN_S1)`, and reenables UART. `rb532_button_poll()` reports `BTN_0`. `rb532_button_probe()` obtains the GPIO, sets polling, and registers the input device.

## Control Flow
Probe gets the named `button` GPIO, creates an input device named `rb532 button`, enables `BTN_0`, configures input polling every 100 ms, and registers. Each poll temporarily steals the shared pin from UART, reads the GPIO value, restores UART mode, reports the value, and syncs.

## State and Persistence Behavior
The driver persists only the GPIO descriptor and input poller. Hardware state is deliberately restored after every poll. Input core persists current button state between poll reports.

## Dependencies and Integration Points
It depends on the RC32434/RB532 platform headers and helper functions, GPIO descriptors, platform device enumeration, and input polling. Userspace sees a host-bus button input device.

## Risks and Edge Cases
Polling disrupts the UART alternate function briefly on every sample. Comments say the GPIO value is inverted, but the implementation reports the raw `gpiod_get_value()` result, so correctness depends on descriptor polarity or hardware behavior. Errors from direction/read/restore helpers are not handled. The polling interval trades latency for UART disturbance.

## Test Signals
Test button press/release while UART is active, GPIO descriptor polarity, polling interval behavior, platform GPIO acquisition failures, and repeated open/close/removal for mode restoration side effects.
