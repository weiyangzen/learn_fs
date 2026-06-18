# sources/distributed-fs/ceph-client/sound/aoa/aoa-gpio.h

## Purpose

This header defines the GPIO abstraction used by Apple Onboard Audio fabrics and codecs to control amplifiers, mute lines, reset pins, and jack-detect notifications independent of the underlying PMF or direct feature-call implementation.

## Important APIs, types, and functions

It defines `notify_func_t`, `enum notify_type`, `struct gpio_methods`, `struct gpio_notification`, and `struct gpio_runtime`. `gpio_methods` covers init/exit, all-amp muting/restoring, headphone/speaker/lineout/master switching, get methods, hardware reset, notification registration, and detect-state reads.

## Control Flow

There is no executable logic. Runtime code fills a `gpio_runtime` with a `gpio_methods` implementation and calls through function pointers. Notifications are represented as delayed work plus callback data and a mutex.

## State and Persistence

`gpio_runtime` stores the selected device node, methods, implementation-private bitfield, and notification records. Implementations persist callback registrations and detect IRQ state.

## Dependencies and Integration Points

It depends on Linux workqueues and mutexes. It is used by AOA core, layout fabric, PMF GPIO, feature-call GPIO, and codec reset/clock-switch code.

## Risks and Test Signals

Risks include NULL method calls, callback lifetime after fabric removal, inconsistent implementation-private bit meanings, and detect notification races. Tests should exercise PMF and feature GPIO implementations, callback register/unregister, amp restore state, and suspend/remove cleanup.
