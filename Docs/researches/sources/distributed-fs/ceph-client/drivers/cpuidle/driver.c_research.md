<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/driver.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/driver.c

## Purpose

`driver.c` manages registration and lookup of cpuidle drivers. It supports both a single global driver and per-CPU drivers under `CONFIG_CPU_IDLE_MULTIPLE_DRIVERS`, normalizes driver state latency/residency fields, and configures tick broadcast support for states that stop local timers.

## Important APIs, Types, And Functions

The file owns `cpuidle_driver_lock`, plus either per-CPU `cpuidle_drivers` or global `cpuidle_curr_driver`. Key functions are `cpuidle_register_driver()`, `cpuidle_unregister_driver()`, `cpuidle_get_driver()`, `cpuidle_get_cpu_driver()`, and `cpuidle_driver_state_disabled()`. Internal helpers include `__cpuidle_driver_init()`, `__cpuidle_set_driver()`, `__cpuidle_unset_driver()`, and `cpuidle_setup_broadcast_timer()`.

## Control Flow

Registering validates the driver and coupled states, rejects disabled cpuidle, fills the default cpumask, converts microsecond and nanosecond latency/residency fields both ways, warns if exit latency exceeds target residency, assigns the driver, enables broadcast timers on all CPUs in the driver's mask when needed, and may switch to a driver-requested governor. Unregistering disables broadcast and restores the previous governor if it had been overridden.

## State And Persistence Behavior

Driver assignment persists globally or per CPU. `drv->bctimer` is set during initialization and cleared at unregister. `cpuidle_driver_state_disabled()` modifies per-device disable bits when devices exist, or marks the driver state unusable before cpumask registration.

## Dependencies And Integration Points

It integrates with tick broadcast, cpumasks, CPU iteration, cpuidle governors, lock-protected driver/device state, and optional multiple-driver support.

## Risks And Test Signals

Risks include driver assignment conflicts, incorrect broadcast enablement on timer-stop states, governor override not restoring, and latency unit conversion mistakes. Test by registering multiple drivers in supported configs, checking broadcast timer setup, toggling driver-disabled states, and verifying governor changes on driver probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/driver.c -->
