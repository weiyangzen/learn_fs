# sources/distributed-fs/ceph-client/drivers/mfd/abx500-core.c

Purpose: Generic ABX500 mixed-signal IC register-access dispatch layer. It lets specific chip cores register an `abx500_ops` implementation and lets child drivers call stable ABX500 helper functions without knowing the physical access backend.

Important APIs, types, and functions: `abx500_register_ops()` stores a devm-managed `abx500_device_entry` in a global list. `abx500_remove_ops()` deletes entries for a device. Exported dispatch functions include `abx500_set_register_interruptible()`, `abx500_get_register_interruptible()`, `abx500_get_register_page_interruptible()`, `abx500_mask_and_set_register_interruptible()`, `abx500_get_chip_id()`, `abx500_event_registers_startup_state_get()`, and `abx500_startup_irq_enabled()`.

Control flow: a chip core such as `ab8500-core.c` registers ops for its parent device. Child drivers pass their device; dispatch looks up `dev->parent` in the global list and invokes the matching callback if present, otherwise returns `-ENOTSUPP`.

State and persistence: state is the global `abx500_list`, containing copied ops and device pointers. Entries are devm-allocated but must be removed from the list explicitly or only remain valid as long as the parent device is live.

Dependencies and integration: depends on Linux device hierarchy, list APIs, devm allocation, exported symbols, and chip-specific `struct abx500_ops` providers.

Risks: global list has no locking, so concurrent registration/removal/lookup can race; devm-managed entries can become stale list nodes if not removed before device cleanup; child lookup assumes exactly one parent level; unsupported callbacks are reported as `-ENOTSUPP`, which callers must handle.

Test signals: register and remove ops, exercise all exported dispatchers from child devices, validate parent lookup failure, run concurrent child access during remove, and use KASAN/lockdep-style tests for stale list entries.
