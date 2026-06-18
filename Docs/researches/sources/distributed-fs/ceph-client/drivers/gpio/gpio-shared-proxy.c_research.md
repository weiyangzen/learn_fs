# sources/distributed-fs/ceph-client/drivers/gpio/gpio-shared-proxy.c

## Purpose
This auxiliary-bus driver presents a shared physical GPIO descriptor as a one-line proxy gpio chip. Multiple users can vote for a high output while the proxy keeps the effective line high until the last high vote is released.

## Important APIs, Types, and Functions
`struct gpio_shared_proxy_data` stores the one-line gpio chip, shared descriptor, device, and this proxy's `voted_high` state. It relies on `struct gpio_shared_desc` and lock helpers from `gpiolib-shared.h`, including shared `usecnt`, `highcnt`, `cfg`, `can_sleep`, and underlying `desc`. The core voting logic is `gpio_shared_proxy_set_unlocked()`.

## Control Flow
Probe obtains a shared descriptor with `devm_gpiod_shared_get()`, creates a one-line gpio chip, chooses sleep-capable or atomic get/set callbacks based on the underlying descriptor, and registers it. Requests/free update shared use count. Direction changes are allowed freely for a single user, but multiple users cannot change an already-output line to input or an already-input line to output. Output set/direction-output use vote accounting so high is shared OR semantics and low removes this proxy's vote.

## State and Persistence
State persists in the underlying GPIO descriptor plus shared descriptor counters protected by a shared lock. This proxy stores whether it currently contributed a high vote. There is no PM state.

## Dependencies and Integration Points
It integrates with the auxiliary bus name `gpiolib_shared.proxy`, GPIO consumer APIs, gpiolib provider APIs, IRQ conversion through `gpiod_to_irq()`, and shared GPIO internals.

## Risks
Configuration changes with multiple users are accepted even when different from existing config, with only debug logging, so users can conflict electrically. Vote accounting assumes request/free and set paths are balanced and serialized by the shared descriptor lock. Direction semantics are intentionally conservative when multiple users exist and may return `-EPERM` for consumers expecting normal GPIO ownership.

## Test Signals
Test single-user direction/value pass-through, multi-user high vote aggregation, repeated high/low votes by the same proxy, final low transition when `highcnt` reaches zero, conflicting direction attempts, set_config conflicts, can-sleep callback selection, and IRQ passthrough.
