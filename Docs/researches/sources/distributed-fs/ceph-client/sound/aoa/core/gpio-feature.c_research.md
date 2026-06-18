# sources/distributed-fs/ceph-client/sound/aoa/core/gpio-feature.c

## Purpose

This file implements AOA GPIO methods using direct PowerMac feature calls to GPIO registers. It controls mute/reset GPIOs, reads jack-detect GPIOs, maps IRQs, and schedules process-context notifications.

## Important APIs, types, and functions

The exported provider is `ftr_gpio_methods`. Key helpers are `get_gpio`, `get_irq`, generated `ftr_gpio_set_*`/`get_*` methods, `ftr_gpio_set_hw_reset`, `ftr_gpio_all_amps_off`, `ftr_gpio_all_amps_restore`, `ftr_handle_notify`, `gpio_enable_dual_edge`, `ftr_gpio_init`, `ftr_gpio_exit`, `ftr_handle_notify_irq`, `ftr_set_notify`, and `ftr_get_detect`. Static globals store GPIO numbers, active states, OF nodes, and IRQ numbers.

## Control Flow

Initialization discovers named GPIO nodes or `audio-gpio` properties, normalizes register offsets, reads active-state properties, enables dual-edge detection, maps IRQs, turns amps off, and initializes delayed work and mutexes. Setters read the GPIO register, update output-enable/output bits according to active state, write the register, and update `implementation_private`. Notification registration serializes per notification, allocates or frees IRQ handlers, and schedules delayed work from IRQ context. Exit unregisters IRQs, cancels work, destroys mutexes, and mutes amps.

## State and Persistence

This implementation uses many file-global GPIO numbers and node pointers, so it effectively supports one active hardware layout. Per-runtime state in `implementation_private` tracks logical amp states for restore. Notification callbacks persist in `gpio_runtime` until unregistered or exit.

## Dependencies and Integration Points

It depends on OF GPIO nodes, OF IRQ mapping, interrupt APIs, PowerMac feature calls, workqueues, and AOA GPIO abstractions. The layout fabric selects this implementation for specific layouts.

## Risks and Test Signals

Risks include global state preventing multiple cards, leaked OF node references from `get_gpio`, IRQ free conditions inconsistent between `notify` and `gpio_private`, active-state inversion mistakes, and no locking around GPIO read-modify-write. Tests should cover all supported GPIO names/aliases, detect IRQ registration, autoswitch notifications, amp restore behavior, and layout remove cleanup.
