# sources/distributed-fs/ceph-client/drivers/input/mouse/gpio_mouse.c

`gpio_mouse.c` is a platform/OF driver that simulates a relative mouse from GPIO lines. Four required GPIOs encode `up`, `down`, `left`, and `right`; three optional GPIOs encode left, middle, and right buttons.

`gpio_mouse_probe()` reads `scan-interval-ms` with a 50 ms fallback, acquires GPIO descriptors with devm helpers, allocates a polled input device, configures relative axes and present buttons, and registers it. `gpio_mouse_scan()` reports button states and computes movement as `right - left` and `down - up` each poll.

State is devm-managed descriptors and scan interval only. Dependencies are platform driver core, firmware properties, OF compatible `"gpio-mouse"`, GPIO descriptor API, and input polling. Risks are pointer speed tied to scan interval, opposite directions cancelling, firmware GPIO polarity mistakes, and missing required lines causing probe failure. Test signals include property parsing, required/optional GPIO behavior, poll interval, capability bits, and `evtest` deltas/buttons.
