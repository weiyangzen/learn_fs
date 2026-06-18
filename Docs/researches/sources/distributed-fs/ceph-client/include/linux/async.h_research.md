# sources/distributed-fs/ceph-client/include/linux/async.h

## Purpose
Declares the kernel asynchronous function-call framework used mainly to improve boot/probe parallelism.

## Important APIs, Types, And Functions
`async_cookie_t` is a 64-bit sequencing cookie. `async_func_t` is the async callback signature. `struct async_domain` tracks pending work and whether the domain participates in global synchronization. `ASYNC_DOMAIN()` and `ASYNC_DOMAIN_EXCLUSIVE()` initialize registered or exclusive domains. Scheduling APIs include `async_schedule_node()`, `async_schedule_node_domain()`, inline `async_schedule()`, `async_schedule_domain()`, `async_schedule_dev()`, `async_schedule_dev_nocall()`, and `async_schedule_dev_domain()`. Synchronization APIs include `async_synchronize_full()`, `async_synchronize_full_domain()`, `async_synchronize_cookie()`, `async_synchronize_cookie_domain()`, `current_is_async()`, and `async_init()`.

## Control Flow, State, And Persistence
Scheduling queues a function and returns a cookie used as a synchronization checkpoint. Domain state is a pending list plus registration flag. Device variants choose a NUMA node from the device. Exclusive domains can go out of scope after their own pending work finishes and do not participate in global full synchronization.

## Dependencies And Integration Points
Depends on list, NUMA, device, and type helpers. Integrated by driver core and subsystem init/probe code that can run independent setup asynchronously.

## Risks And Test Signals
Async callbacks must not outlive data or domain lifetime. Missing synchronization before freeing resources can cause use-after-free. Tests should cover global and domain-specific waits, cookie ordering, device NUMA scheduling, exclusive-domain lifetime, atomic-context scheduling, and `current_is_async()` behavior.
