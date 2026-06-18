# sources/distributed-fs/ceph-client/sound/aoa/core/gpio-pmf.c

## Purpose

This file implements AOA GPIO methods using PowerMac platform functions (PMF). It provides amp mute, reset, jack detection, and notification callbacks for layouts where PMF functions describe audio GPIO behavior.

## Important APIs, types, and functions

The exported provider is `pmf_gpio_methods`. Generated setters/getters cover headphone, amp/speakers, and lineout. Other important functions are `pmf_gpio_set_hw_reset`, `pmf_gpio_all_amps_off`, `pmf_gpio_all_amps_restore`, `pmf_handle_notify`, `pmf_gpio_init`, `pmf_gpio_exit`, `pmf_handle_notify_irq`, `pmf_set_notify`, and `pmf_get_detect`.

## Control Flow

Setters call named PMF functions like `headphone-mute`, passing inverted logical state for mute, then update `implementation_private`. Init mutes amps and initializes delayed work and mutexes. Notification registration allocates a `pmf_irq_client`, registers it against a named detect function, stores it as `gpio_private`, and schedules delayed work from the PMF IRQ handler. Removal unregisters PMF IRQ clients, cancels work, frees clients, and mutes amps.

## State and Persistence

Per-runtime `implementation_private` stores logical output states. `gpio_notification.gpio_private` owns PMF IRQ client allocations while notifications are active.

## Dependencies and Integration Points

It depends on PowerMac PMF APIs, AOA GPIO abstractions, workqueues, mutexes, and slab allocation. The layout fabric selects this implementation for most layouts.

## Risks and Test Signals

Risks include missing PMF functions, inverted mute semantics, notification client leaks, detect calls returning platform-specific values, and callback races during exit. Tests should cover PMF call failures, register/unregister notifications, detect reads, amp restore, and suspend/remove cleanup.
