# sources/distributed-fs/ceph-client/drivers/media/cec/core/cec-core.c

Purpose: This file owns CEC device-node registration, adapter allocation/registration/unregistration/deletion, module parameters, debugfs setup, bus/chrdev initialization, and optional RC input-device allocation.

Important APIs, types, and functions: Exported APIs are `cec_allocate_adapter()`, `cec_register_adapter()`, `cec_unregister_adapter()`, and `cec_delete_adapter()`. Internal functions include `cec_devnode_register()`, `cec_devnode_unregister()`, `cec_devnode_release()`, debugfs `cec_error_inj_*` handlers, and module init/exit `cec_devnode_init()`/`cec_devnode_exit()`. Global state includes `cec_debug`, `debug_phys_addr`, `cec_dev_t`, `cec_devnode_nums`, `cec_devnode_lock`, `cec_bus_type`, and `top_cec_dir`.

Control flow and state: Allocation validates caps/ops/available LAs, initializes adapter fields and queues, starts the main adapter kthread, and optionally creates an RC device. Registration attaches the adapter to a parent device, sets transfer timeout, registers RC if present, allocates a minor, initializes cdev/device state, creates debugfs entries, and stores adapter drvdata. Unregistration removes RC, debugfs, notifier connection, invalidates addresses/logical addresses, disables the adapter, removes the cdev/device, and drops the final device reference. Device release frees the minor and calls `cec_delete_adapter()`, which stops config/main kthreads, invokes driver `adap_free`, frees RC leftovers, and releases memory.

State and persistence behavior: Device minor allocation is process-global and protected by `cec_devnode_lock`. Adapter state is volatile and lifetime-managed by char-device references. Debugfs exposes status and optional error injection but does not persist settings across adapter teardown.

Dependencies and integration points: Integrates with Linux char devices, device model, bus registration, debugfs, kthreads, optional RC core, CEC notifier, and `cec_devnode_fops` from `cec-api.c`. Driver authors use this file’s exported allocation/register/unregister/delete lifecycle.

Risks and edge cases: Lifecycle ordering is critical: after successful `cec_register_adapter()`, drivers should call `cec_unregister_adapter()` rather than direct delete. Minor exhaustion, failure paths around RC registration/cdev registration, open filehandles during unregister, config kthread shutdown, and debugfs error-injection parsing are important risk areas. `debug_phys_addr` can expose physical-address capability for debug and changes userspace behavior.

Test signals: Exercise adapter probe/remove failure paths, repeated register/unregister, open fd during remove, RC integration enabled/disabled, debugfs status/error-injection availability, minor reuse across 256-device boundary tests, and module unload with active adapters.
