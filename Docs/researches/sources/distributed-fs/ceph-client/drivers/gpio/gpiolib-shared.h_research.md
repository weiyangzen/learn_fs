# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-shared.h

## Purpose
`gpiolib-shared.h` declares the internal and consumer-facing pieces of the shared GPIO infrastructure. It provides gpiochip setup/teardown hooks, proxy lookup installation, the shared descriptor object, a managed getter, and lock helpers for safe shared access.

## Important APIs, Types, And Functions
When `CONFIG_GPIO_SHARED` is enabled, it declares `gpiochip_setup_shared()`, `gpio_device_teardown_shared()`, and `gpio_shared_add_proxy_lookup()`. Otherwise these are inline no-ops returning success. `struct gpio_shared_desc` contains the real descriptor, sleep capability, cached config/use counters, high counter, and either a mutex or spinlock. `devm_gpiod_shared_get()` returns a managed shared descriptor. `DEFINE_LOCK_GUARD_1(gpio_shared_desc_lock, ...)` provides scoped locking, and `gpio_shared_lockdep_assert()` verifies the correct lock is held.

## Control Flow
Generic gpiochip code can call setup and teardown regardless of configuration. Shared GPIO consumers acquire `struct gpio_shared_desc` through devres and use the guard macro to take either the mutex or spinlock depending on `can_sleep`.

## State And Persistence
The header-defined `struct gpio_shared_desc` is persistent per shared entry while references exist. The lock union is initialized by implementation code according to whether the GPIO can sleep.

## Dependencies And Integration Points
It depends on cleanup guards, lockdep, mutexes, spinlocks, and GPIO/device forward declarations. It integrates shared GPIO implementation with gpiochip lifecycle code and proxy consumers.

## Risks
Consumers must use the correct shared lock before modifying shared descriptor counters or configuration. No-op stubs mean callers must not assume proxy behavior when `CONFIG_GPIO_SHARED` is disabled.

## Test Signals
Build-test enabled and disabled configurations, lockdep assertions for sleep and non-sleep GPIOs, managed get/put lifetime, and gpiochip setup/teardown calls in generic registration paths.
