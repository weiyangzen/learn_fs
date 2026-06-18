# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-ncp5623.c

Purpose: I2C multicolor LED driver for ON Semiconductor NCP5623 triple-output RGB controller. It supports global brightness and simple hardware dimming patterns.

Important APIs, types, and functions: `struct ncp5623` stores I2C client, multicolor class device, mutex, current brightness, and a jiffies delay guard while dimming is in progress. `ncp5623_write()` performs the chip's command-style SMBus write. `ncp5623_brightness_set()` writes per-channel PWM intensity, disables dimming time, and writes global current. `ncp5623_pattern_set()` programs an upward/downward step or direct brightness change and calculates when the hardware transition should finish.

Control flow: probe requires a named `multi-led` child node, allocates subled metadata from its children, initializes callbacks and default `pattern` trigger, registers the multicolor LED, and stores client data. Brightness and pattern writes are rejected with `-EBUSY` while a prior dimming transition is still in progress.

State and persistence: `current_brightness` mirrors the global brightness target; `delay` prevents overlapping hardware transitions. Remove clears delay, disables dimming time, unregisters, and destroys the mutex. Shutdown sends chip shutdown unless LED core retention is requested.

Dependencies and integration points: I2C SMBus, LED multicolor/pattern APIs, firmware child-node parsing, jiffies timing, and compatible `onnn,ncp5623`.

Risks and test signals: test busy-window timing, dimming time constraints and 8 ms granularity, brightness-difference edge case of one step, subled parsing failures with fwnode release, shutdown retention flag, and behavior when brightness is set during hardware fade.
