<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-gpio.c

## Purpose

This file implements the Turris Omnia MCU GPIO and nested IRQ controller. It exposes status/control bits as 64 GPIOs, maps MCU interrupt bits to GPIO IRQs, supports old and new MCU interrupt APIs, and adds a `front_button_mode` sysfs attribute.

## Important APIs, Types, And Functions

`struct omnia_gpio` describes command, control command, status bit, control bit, interrupt bit, and feature requirements. `omnia_gpios[]` and `omnia_int_to_gpio_idx[]` are the central hardware maps. GPIO callbacks implement request, direction, get, get-multiple, set, set-multiple, valid masks, and OF translation. IRQ callbacks maintain `mask`, `rising`, `falling`, `both`, cached values, and hardware masks. `omnia_irq_read_pending_new()` reads `OMNIA_CMD_GET_INT_AND_CLEAR`; `omnia_irq_read_pending_old()` derives edges from status-word deltas. `omnia_mcu_register_gpiochip()` registers the gpiochip and requests the parent MCU IRQ.

## Control Flow

Registration initializes the mutex, gpiochip methods, IRQ chip data, valid-mask callbacks, and optional old-firmware status cache/work item. Runtime GPIO reads group I2C status commands where possible. GPIO writes send general or extended control commands. IRQ mask/type updates alter software bitmaps and, with new firmware, synchronize interleaved rising/falling masks to the MCU. The threaded parent IRQ reads pending bits, maps them through the gpiochip IRQ domain, and calls `handle_nested_irq()`.

## State And Persistence

The MCU state includes GPIO control bits and interrupt masks in firmware. Kernel state caches IRQ masks, edge configuration, both-edge cached values, old-firmware last status, and front-button release emulation state. `front_button_mode` changes MCU control state.

## Dependencies And Integration Points

It depends on gpiolib, gpiolib IRQCHIP, OF GPIO translation with three cells, I2C command helpers, feature bits from the MCU interface header, workqueues, and optional consumers such as TRNG and keyctl using `omnia_mcu_request_irq()`.

## Risks

Hardware maps are dense and feature-dependent; wrong bit mappings affect power rails, reset lines, LEDs, and interrupts. `front_button_mode_store()` calls the locked control helper without taking the mutex, relying on helper naming rather than lock enforcement. Old firmware emulates button release and ignores stuck overcurrent bits, so behavior differs by feature bit. `omnia_mcu_request_irq()` uses the first set bit in `spec`; multi-bit specs would select only one interrupt.

## Test Signals

Test GPIO valid masks by feature bitmap, OF translation banks, input/output direction, PHY SFP auto/manual direction, get/set multiple, new interrupt mask programming, old firmware edge derivation, button release emulation, nested IRQ delivery for TRNG/signing/front button, and sysfs front-button mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-gpio.c -->
