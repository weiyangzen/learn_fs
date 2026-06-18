# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_datagram.c

Purpose: implements VMCI datagram endpoints, endpoint lifetime, routing dispatch, host callback invocation, guest hypercall forwarding, and exported datagram APIs.

Important APIs/functions: `vmci_datagram_create_handle_priv()` and `vmci_datagram_create_handle()` allocate a host datagram endpoint as a VMCI resource with callback, flags, client data, and privilege flags. `vmci_datagram_destroy_handle()` removes the resource and frees the endpoint. `vmci_datagram_send()` dispatches a caller-provided datagram. Internal `vmci_datagram_dispatch()` validates datagram size, calls `vmci_route()`, and selects host or guest dispatch. `vmci_datagram_invoke_guest_handler()` invokes a local guest endpoint for datagrams read from the device.

Control flow: host dispatch rejects hypervisor destinations, checks source ownership, resolves source privileges, then either invokes a host resource callback, queues delayed work, handles hypervisor event datagrams, or copies the datagram to a VM context queue. Guest dispatch validates that the source endpoint exists, then sends through `vmci_send_datagram()`. Delayed callbacks keep a resource reference until work completion and optionally count against `delayed_dg_host_queue_size`.

State/persistence: datagram endpoint state is a `datagram_entry` in the global resource table. Delayed host-to-host callbacks are bounded by `VMCI_MAX_DELAYED_DG_HOST_QUEUE_SIZE`. No persistent state exists beyond in-memory resources and scheduled work.

Dependencies/integration: relies on `vmci_resource` for lookup/lifetime, `vmci_route` for personality selection, `vmci_context` for VM queue delivery and privileges, `vmci_guest` for hypervisor send, and `vmci_event` for event datagrams.

Risks: delayed queue limit uses `atomic_add_return() == max`, allowing max-1 but not clearly guarding values greater than max under unusual races. Callback execution context differs by flags and by host-to-host delivery, so clients must tolerate process/workqueue context. Destroy removes the resource after dropping one lookup reference; delayed work safety depends on resource references.

Test signals: create/destroy endpoint with duplicate handles, invalid flags, ANYCID flags, host-to-host delayed delivery, guest route send failure, no-handle guest callback, VM-to-VM rejection, privilege-denied delivery, and payload-size boundary cases.
