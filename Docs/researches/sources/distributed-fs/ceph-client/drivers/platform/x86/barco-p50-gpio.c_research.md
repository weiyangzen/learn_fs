# sources/distributed-fs/ceph-client/drivers/platform/x86/barco-p50-gpio.c

## Purpose
`barco-p50-gpio.c` supports EC-connected identify LED and identify button GPIOs on Barco P50 boards. It translates a small EC mailbox over legacy I/O ports into a two-line GPIO chip, then instantiates standard `leds-gpio` and `gpio-keys-polled` consumers using software nodes.

## Important APIs, Types, And Functions
`struct p50_gpio` embeds the `gpio_chip`, a mutex for serialized EC mailbox access, the I/O port base, and child platform devices for LEDs and keys. Low-level helpers `p50_wait_ec()`, `p50_read_mbox_reg()`, and `p50_write_mbox_reg()` operate on ports `0x299` and `0x29a`. `p50_wait_mbox_idle()` and `p50_send_mbox_cmd()` implement the mailbox protocol with command, status, parameter, and data registers.

The GPIO callbacks are `p50_gpio_get_direction()`, `p50_gpio_get()`, and `p50_gpio_set()`. The LED line is output-only and the button line is input-only. Software nodes describe the LED as `identify` and the button as a polled `KEY_VENDOR` GPIO key.

## Control Flow
Module init DMI-matches Barco P50, registers the platform driver, and creates a simple platform device with the I/O resource. Probe reserves the I/O region, allocates state, initializes the GPIO chip, clears the mailbox, registers the gpiochip, registers software nodes, and creates `leds-gpio` and `gpio-keys-polled` child devices. Remove unregisters child devices and software nodes.

GPIO get/set operations lock the mutex, send a read or write mailbox command with the line-specific parameter, and read or write the mailbox data register. Mailbox status must report success or the operation returns `-EIO`.

## State And Persistence
The kernel stores only GPIO chip registration state and child device handles. LED/button values live in the EC. The mailbox is cleared at probe to remove stale commands. There is no suspend-specific state and no persistent configuration.

## Dependencies And Integration Points
The driver uses DMI, raw I/O port access, gpiochip, GPIO consumer software nodes, property APIs, `leds-gpio`, `gpio-keys-polled`, input event codes, and platform devices. It deliberately exports generic GPIO lines so standard LED and key drivers provide user-visible behavior.

## Risks
The mailbox uses polling loops and raw I/O, so timeouts or incorrect port ownership can block GPIO operations and return errors. `p50_gpio_get()` and `p50_gpio_set()` index `gpio_params[offset]`; callers are expected to pass valid GPIO offsets through gpiolib, but defensive bounds are limited to direction handling. Software-node and child-device cleanup ordering matters after partial probe failures.

## Test Signals
Test DMI gating, I/O region reservation failure, mailbox idle timeout handling, LED GPIO set/readback, button GPIO polling as `KEY_VENDOR`, software-node registration failure unwinding, child device registration failure unwinding, and module unload cleanup.
