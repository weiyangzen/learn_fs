# sources/distributed-fs/ceph-client/drivers/staging/greybus/gpio.c

## Purpose
Greybus GPIO bridged-PHY child driver. It presents remote Greybus GPIO lines as a Linux `gpio_chip` with optional IRQ support.

## Important APIs, Types, And Functions
`struct gb_gpio_controller` holds the `gbphy_device`, connection, line count, line state array, `gpio_chip`, `irq_chip`, and IRQ mutex. `struct gb_gpio_line` caches active, direction, value, debounce, IRQ type, and pending mask/type changes. Greybus operation helpers cover line count, activate/deactivate, get/set direction, get/set value, debounce, IRQ mask/unmask/type. Linux callbacks include `gb_gpio_request()`, `gb_gpio_free()`, `gb_gpio_get_direction()`, `gb_gpio_direction_input/output()`, `gb_gpio_get/set()`, and `gb_gpio_set_config()`.

## Control Flow
Probe creates a connection with `gb_gpio_request_handler()`, enables TX only, queries line count, initializes irqchip/gpiochip callbacks, enables full RX/TX, registers the gpiochip, and releases the initial gbphy PM reference. Unsolicited `GB_GPIO_TYPE_IRQ_EVENT` requests validate payload and line number, find the mapped Linux IRQ, and call `generic_handle_irq_safe()`.

## State And Persistence
Line state is cached per line but authoritative state lives on the module. IRQ mask/type changes are staged in `gb_gpio_irq_mask()`, `gb_gpio_irq_unmask()`, and `gb_gpio_irq_set_type()`, then sent under `irq_lock` from `gb_gpio_irq_bus_sync_unlock()`. No persistent storage exists.

## Dependencies And Integration Points
Uses `gbphy` runtime PM, Greybus GPIO protocol, Linux GPIO/IRQ domain APIs, `gpiochip_add_data()`, and generic IRQ handling.

## Risks
Line indexes are cast to `u8`; correctness depends on remote line count fitting protocol limits. IRQ staging must remain synchronized with the irqchip bus lock/unlock contract. Remove disables RX before `gpiochip_remove()` to prevent events racing with teardown.

## Test Signals
Test line-count discovery, each GPIO operation, debounce bounds, IRQ type mapping for all Linux IRQ types, unsolicited bad payloads and invalid lines, remove during active IRQs, PM get failures, and gpiochip registration failure unwinds.
