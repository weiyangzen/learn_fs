# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec.h

Purpose: private header declaring the core Chrome EC APIs used by bus transports and related platform code.

Important APIs, types, and functions: forward declares `struct cros_ec_device` and `struct device`, and declares allocation, registration/unregistration, suspend/resume stage helpers, and `cros_ec_irq_thread()`.

Control flow: transport drivers include this header, allocate an EC device, assign transport callbacks, register with the core, and wire PM ops to the suspend/resume helpers. Event-only transports can call `cros_ec_irq_thread()` when their bus-specific event notification arrives.

State and persistence: no storage; it defines cross-file contracts for state owned by `struct cros_ec_device`.

Dependencies and integration points: includes `linux/interrupt.h` for `irqreturn_t`. It is internal to `drivers/platform/chrome`, not the public protocol header.

Risks and edge cases: the header exposes only high-level lifecycle functions; transports must still know public `cros_ec_device` fields from platform-data headers. Missing declarations here would cause bus drivers to duplicate externs.

Test signals: compile coverage for all Chrome EC transports and PM configurations.
