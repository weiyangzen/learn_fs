# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_driver.c

Purpose: module entry point and personality coordinator for the unified VMCI driver. It initializes event support, guest PCI personality, host misc-device personality, module parameters, and VSOCK transport activation callbacks.

Important APIs/functions: `vmci_get_context_id()` returns the guest VM CID when the guest device is active, otherwise host CID when host personality is active. `vmci_register_vsock_callback()` registers or unregisters the VSOCK transport callback and immediately calls it for already active personalities. `vmci_call_vsock_callback()` ensures host callback is called only once. `vmci_drv_init()` initializes events and enabled personalities. `vmci_drv_exit()` tears them down in reverse order.

Control flow: module load initializes the event subsystem first, then attempts guest and host init unless disabled by `disable_guest` or `disable_host`. If neither personality initializes, it exits with `-ENODEV` and shuts down events. Module unload exits initialized personalities and events. VSOCK callback state is serialized by `vmci_vsock_mutex`.

State/persistence: module-global booleans track parameter disables and whether each personality was initialized. Callback pointer and host-callback-called state are process-lifetime globals only.

Dependencies/integration: calls `vmci_event_init/exit`, `vmci_guest_init/exit`, `vmci_host_init/exit`, `vmci_guest_code_active()`, `vmci_host_code_active()`, and VSOCK exported callback registration.

Risks: `vmci_get_context_id()` prioritizes guest personality when both host and guest are active, which is intentional but affects clients expecting host CID in unified mode. Failed host/guest init is warning-only unless both fail. Callback registration allows only one callback and returns `-EBUSY` for duplicates.

Test signals: module parameter combinations, guest-only/host-only/both-disabled load behavior, VSOCK callback registration/unregistration, callback replay for already active personalities, and host callback single-call behavior.
