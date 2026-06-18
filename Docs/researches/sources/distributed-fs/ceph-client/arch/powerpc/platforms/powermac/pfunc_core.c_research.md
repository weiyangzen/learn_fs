# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/pfunc_core.c

Purpose: implements the platform-function bytecode parser, registry, invocation, reference management, and IRQ-client dispatch used by PowerMac device-tree `platform-do-*` properties.

Important APIs/types/functions: command parsing uses `pmf_cmd`, `pmf_next32`, `pmf_next_blob`, `pmf_parse_one`, and the `pmf_parsers` table for opcodes such as GPIO, register, I2C, config-space, delays, shifted/masked reads, shifted/masked writes, and mask-and-compare. Registry types are `pmf_device`, `pmf_function`, and `pmf_irq_client`. Exported APIs include `pmf_register_driver`, `pmf_unregister_driver`, `pmf_get_function`, `pmf_put_function`, `pmf_find_function`, `pmf_call_function`, `pmf_call_one`, `pmf_do_functions`, `pmf_register_irq_client`, `pmf_unregister_irq_client`, and `pmf_do_irq`.

Control flow: a driver registers handlers for an OF node. Registration scans all properties named `platform-do-*`, creates one or more `pmf_function` records per property, does a parse-only pass to determine each function length, and links the device into the global registry. Callers either find one on-demand function through a target node and optional phandle indirection, or run all matching functions on a registered node for a flag set such as init, sleep, wake, or interrupt generation. Invocation optionally calls a handler `begin`, parses and executes bytecode commands against the handler table, and then calls `end`.

State and persistence: global lists `pmf_devices` and per-device `functions` hold live registrations. `kref` protects device and function lifetimes, and module references protect handler owners during calls. `pmf_lock` serializes registry and IRQ-client list access; `pmf_irq_mutex` serializes IRQ enable/disable list transitions. There is no disk persistence.

Dependencies/integration: this is the common engine used by `pfunc_base.c`, `low_i2c.c`, device drivers that consume platform functions, OF property/phandle lookup, and module ownership. Handler behavior is supplied by the registering subsystem, so PMF core is intentionally transport-agnostic.

Risks: file comments call out incomplete race-free locking. `pmf_do_irq` holds the spinlock while invoking client handlers, so handlers must be IRQ-safe and bounded. Parse-only and execute passes depend on correct bytecode length calculation; malformed properties return `-ENXIO` and may stop adding later functions. Several opcodes are unimplemented. `pmf_call_one` calls `end` even if `begin` fails and returns `NULL`, relying on handlers to tolerate that.

Test signals: register drivers with multiple `platform-do-*` functions; malformed/truncated bytecode and unknown opcodes; phandle-directed function lookup; flag filtering for on-init/on-sleep/on-wake/on-demand/interrupt; begin/end lifecycle on success and failure; module refcount behavior; IRQ client first-enable/last-disable and dispatch under concurrent registration.
