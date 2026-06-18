# sources/distributed-fs/ceph-client/drivers/leds/leds-ipaq-micro.c

Purpose: notification LED subdevice driver for iPAQ h3xxx Atmel micro companion MFD.

Important APIs/types/functions: `micro_leds_brightness_set()` and `micro_leds_blink_set()` construct `struct ipaq_micro_msg` with `MSG_NOTIFY_LED` and four command bytes. A single static `led_classdev micro_led` provides blocking brightness, hardware blink, and suspend/resume flag.

Control flow: probe registers the static LED classdev. Brightness ON sends green LED on-time 0 and off-time 1 decisecond; OFF sends on-time 1 and off-time 0, reflecting firmware special meaning of zero as 256 deciseconds. Blink validates max 25.6 s delays, supplies 100/100 ms default when both are zero, rounds ms to deciseconds, and transmits synchronously.

State and persistence: no private driver allocation. Firmware stores notification timing after each sync message. LED core tracks requested values.

Dependencies/integration: iPAQ micro MFD parent data is reached via `led_cdev->dev->parent->parent`, and messages go through `ipaq_micro_tx_msg_sync()`.

Risks: the parent-pointer chain is fragile if device hierarchy changes. Only green LED is controlled; yellow behavior is documented but not exposed. Delay conversion can round small nonzero values to zero, which firmware treats specially.

Test signals: verify MFD parent lookup, ON/OFF command bytes, blink default and max validation, decisecond rounding, and synchronous error propagation from `ipaq_micro_tx_msg_sync()`.
