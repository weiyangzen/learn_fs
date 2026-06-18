# sources/distributed-fs/ceph-client/include/linux/device/devres.h

Purpose: Defines managed device-resource APIs that bind allocations, mappings, pages, per-CPU memory, and cleanup actions to a device lifetime.

Important APIs, types, and functions: Defines `dr_release_t`, `dr_match_t`, raw `devres_alloc/free/add/find/get/remove/destroy/release`, group APIs, managed allocation helpers (`devm_kmalloc`, `devm_kzalloc`, arrays, `devm_krealloc`, memdup, kstrdup, kasprintf), managed per-CPU/page allocation, managed I/O mapping helpers, custom action APIs (`devm_add_action`, `devm_add_action_or_reset`, remove/release/is_added), and `CONFIG_HAS_IOMEM` stubs.

Control flow: Drivers allocate resources with devm helpers or create explicit devres records. The driver core releases records automatically when the device unbinds or when a group is released. Groups provide transactional probe error handling; `devm_add_action_or_reset()` runs the action immediately if registration fails.

State and persistence: Device-owned `devres_head` and `devres_lock` in `struct device` store resource records. State persists only until explicit removal or device teardown.

Dependencies and integration points: Depends on error pointers, GFP flags, NUMA, overflow helpers, percpu allocation, resources, I/O memory, and device core teardown. Used heavily by probe/remove paths to reduce manual cleanup.

Risks and test signals: Risks include mixing devm and manual frees, wrong match callbacks removing another resource, action/data mismatch, group leaks on probe failure, and silent `devm_add_action()` failure if not checked. Test probe failure unwind, remove ordering, devres groups, managed I/O map disabled builds, allocation overflow handling, and action-or-reset paths.
