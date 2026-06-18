# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic.h

Purpose: small shared identity header for the Cisco usNIC verbs driver.

Important APIs/data: defines `DRV_NAME` as `usnic_verbs`, the Cisco VIC userspace NIC PCI device ID `0x00cf`, and driver version/date strings.

Control flow: included by logging, main, debugfs, and other usNIC files to keep module names, PCI IDs, and build-info output consistent.

State and persistence: no mutable state.

Dependencies and integration: provides the PCI ID used by `usnic_ib_main.c` and strings used by module metadata/debugfs/logging.

Risks: stale version/date strings can mislead operators. Changing `DRV_NAME` affects PCI region request names, debugfs root, and log prefixes.

Test signals: module metadata, debugfs build-info output, PCI probe matching, and log prefix consistency.
