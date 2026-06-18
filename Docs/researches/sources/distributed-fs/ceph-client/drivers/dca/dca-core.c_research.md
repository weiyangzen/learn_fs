# sources/distributed-fs/ceph-client/drivers/dca/dca-core.c

Purpose: Intel DCA broker that connects requester devices with DCA providers, grouped by PCI root complex, and exports provider/requester/tag APIs.

Important APIs/types/functions: `dca_add_requester()`, `dca_remove_requester()`, `dca3_get_tag()`, legacy `dca_get_tag()`, `alloc_dca_provider()`, `free_dca_provider()`, `register_dca_provider()`, `unregister_dca_provider()`, notifier registration, domain helpers, and `dca_init()/exit()`.

Control flow and state: global `dca_domains` holds provider lists per PCI root complex under `dca_lock`; provider add/remove events use a blocking notifier chain. Requesters are added by finding a provider that manages the device, calling provider ops to allocate a slot, and creating sysfs requester devices. Providers create sysfs provider devices before joining a domain; IOAT v3 blocking logic prevents unsupported multi-root/provider configurations and can unregister existing providers.

Dependencies and integration: depends on PCI root-complex discovery, provider ops from `<linux/dca.h>`, sysfs helper functions in `dca-sysfs.c`, raw spinlocks, blocking notifiers, and exported symbols for other drivers.

Risks and test signals: lock dropping during provider registration, provider/domain teardown, sysfs rollback, legacy `dca_get_tag(NULL)` behavior, IOAT provider blocking, and notifier order are key. Test multiple providers, multiple PCI roots, requester add/remove rollback, get_tag before/after removal, notifier clients, module unload, and sysfs device cleanup.
