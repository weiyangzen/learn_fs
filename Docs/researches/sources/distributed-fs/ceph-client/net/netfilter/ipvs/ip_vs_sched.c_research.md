# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sched.c

## Purpose
Provides the central registry and binding logic for IPVS schedulers. It lets services bind to scheduler modules, autoload schedulers by name, track module references, and format common scheduler error messages.

## Important APIs, Types, and Functions
`ip_vs_bind_scheduler()` calls a scheduler's `init_service()` and publishes it with RCU. `ip_vs_unbind_scheduler()` calls `done_service()`. `ip_vs_scheduler_get()` looks up a scheduler by name and autoloads `ip_vs_<name>` if needed. `ip_vs_scheduler_put()` releases module references. `register_ip_vs_scheduler()` and `unregister_ip_vs_scheduler()` manage the global list under `ip_vs_sched_mutex`. `ip_vs_scheduler_err()` prints service-specific rate-limited errors and is exported.

## Control Flow
Scheduler modules register their static `struct ip_vs_scheduler` during module init. Service configuration obtains a scheduler by name, which tries `try_module_get()` atomically while scanning the list. Binding initializes per-service scheduler data before assigning `svc->scheduler`. Unregister removes the scheduler from the list and decrements the IPVS use count; module exit code usually waits for RCU readers.

## State and Persistence
Global state is the `ip_vs_schedulers` list and module/IPVS use counts. Per-service state is owned by each scheduler but its lifecycle is initiated here. The registry persists for the IPVS module lifetime.

## Dependencies and Integration Points
Depends on Linux modules, request_module, mutexes, RCU pointer assignment, IPVS service structures, and IPVS global use counting. Every scheduler module in this subset registers through this file.

## Risks
Binding does not roll back partial scheduler init except by returning the init error; scheduler implementations must clean up their own failed init paths. `ip_vs_unbind_scheduler()` assumes the caller controls setting `svc->scheduler` to NULL. Registry uniqueness is name-based. Scheduler modules must synchronize RCU after unregistering if readers can still hold callbacks.

## Test Signals
Load schedulers by name, autoload missing modules, bind and unbind services, duplicate scheduler registration, unregister while services are draining, IPv4/IPv6/fwmark error formatting, and failure injection in scheduler `init_service()`.
