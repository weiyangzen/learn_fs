# sources/distributed-fs/ceph-client/drivers/leds/leds-qnap-mcu.c

Purpose: LED class integration for LEDs controlled by QNAP MCU devices. It exposes per-drive red error LEDs, an optional USB blue LED, and a dual red/green status LED pair by translating LED core brightness/blink callbacks into MCU command bytes.

Important APIs, types, and functions: `struct qnap_mcu_err_led`, `struct qnap_mcu_usb_led`, and `struct qnap_mcu_status` hold LED class devices and MCU state. `qnap_mcu_err_led_set()` and `_blink_set()` emit `@R` commands per drive. `qnap_mcu_usb_led_set()` and `_blink_set()` emit `@C` commands whose third byte is shared with buzzer control. `qnap_mcu_status_led_encode()` maps combined red/green modes to the MCU's single status-code byte. `qnap_mcu_leds_probe()` creates devices based on `struct qnap_mcu_variant`.

Control flow: platform probe gets the parent `struct qnap_mcu` and variant platform data, registers an error LED for each drive, conditionally registers the USB LED, then registers the two status LEDs. Brightness callbacks avoid disrupting existing blink modes when brightness remains nonzero. Blink callbacks coerce requested timing to the MCU-supported fast/slow values and update local mode before sending an acknowledged command.

State and persistence: each LED caches its MCU mode in RAM. The MCU holds the durable hardware state until new commands arrive. There is no remove-time restore. The status LEDs share a single MCU command path, so the red and green LED objects coordinate through the parent `qnap_mcu_status`.

Dependencies and integration points: depends on the QNAP MCU MFD interface and `qnap_mcu_exec_with_ack()`, LED class APIs, platform data from the parent variant, and uleds name-size constants.

Risks and test signals: the status LED pointer trick (`statusled_to_qnap_mcu_status()` via each member's `red` pointer) is subtle and should be tested with both red and green callbacks. Exercise blink/brightness transitions, especially nonzero brightness while blink is active, off-then-blink no-op behavior, and command-byte overlap with the input/buzzer driver for the USB LED.
