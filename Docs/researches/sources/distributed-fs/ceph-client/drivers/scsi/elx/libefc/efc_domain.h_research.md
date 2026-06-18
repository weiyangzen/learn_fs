# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.h

## Purpose
`efc_domain.h` declares the public domain state-machine API and frame-dispatch hooks for libefc.

## Important APIs, Types, And Functions
Exports include domain allocation/free, all domain state handlers, `efc_domain_attach`, `efc_domain_post_event`, `__efc_domain_attach_internal`, `efc_domain_dispatch_frame`, and `efc_node_dispatch_frame`.

## Control Flow And State
The header lays out the expected domain lifecycle: init after a domain-found callback, wait for hardware allocation, attach with an FC_ID, become ready, then wait for child nports and hardware shutdown on loss. Dispatch declarations show that domain-level receive classification routes frames to node-level handlers.

## Dependencies And Integration Points
It depends on `struct efc_domain`, `struct efc_sm_ctx`, `enum efc_sm_event`, and `struct efc_hw_sequence` from `efclib.h`. Hardware and transport code call into `efc_domain_cb`/`efc_dispatch_frame`, while node/fabric code calls `efc_domain_attach`.

## Risks And Test Signals
Risks include callers posting events to an uninitialized `drvsm` or dispatching frames before `efc->domain` is attached. Test signals include state transition traces across each declared handler and receive-frame tests that validate the domain-to-node dispatch contract.
