<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi_api.h -->
# sources/distributed-fs/ceph-client/include/linux/msi_api.h

## Purpose
`msi_api.h` exposes the small driver-relevant MSI API for mapping MSI indices to Linux virtual IRQ numbers and carrying implementation-specific instance cookies.

## Important APIs, Types, and Functions
It defines `enum msi_domain_ids` with `MSI_DEFAULT_DOMAIN` and `MSI_MAX_DEVICE_IRQDOMAINS`, `union msi_instance_cookie`, `struct msi_map`, `MSI_ANY_INDEX`, `msi_domain_get_virq()`, and inline `msi_get_virq()`.

## Control Flow and State
Drivers or subsystem code query a device/domain/index mapping through `msi_domain_get_virq()` or the default-domain wrapper. Allocation APIs elsewhere may return `struct msi_map`, where negative `index` carries an error.

## State and Persistence Behavior
No state is stored here. It references MSI mappings maintained by the MSI core.

## Dependencies and Integration Points
It is included by `msi.h` and driver code that only needs safe lookup-level access.

## Risks
Callers must distinguish missing mapping (`0` virq) from valid IRQs and negative allocation errors in `msi_map.index`. Domain IDs are intentionally bounded.

## Test Signals
Driver MSI lookup tests, default and non-default domain mappings, dynamic index allocation with `MSI_ANY_INDEX`, and disabled/no-mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msi_api.h -->
