# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_route.h

Purpose: declares the VMCI route enum and route-selection helper.

Important APIs/types: `enum vmci_route` has `VMCI_ROUTE_NONE`, `VMCI_ROUTE_AS_HOST`, and `VMCI_ROUTE_AS_GUEST`. `vmci_route()` decides the route for source/destination handles and may normalize an invalid source context.

Control flow/integration: datagram and queue-pair code include this header to avoid duplicating personality-selection logic.

State/persistence: no state.

Risks: route enum additions would require updates to all dispatch switch/if logic. Callers must pass mutable source handles because the function can fill the context.

Test signals: compile coverage for every route consumer and unit-style matrix tests for host/guest/personality combinations.
