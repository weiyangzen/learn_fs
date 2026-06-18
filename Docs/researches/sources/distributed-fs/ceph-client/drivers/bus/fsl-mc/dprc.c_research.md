# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/dprc.c

## Purpose
Provides the DPAA2 Data Path Resource Container command API wrappers used to communicate with Management Complex firmware. It covers opening/closing containers, resetting child containers, IRQ configuration, object enumeration, region lookup, API versioning, container ID lookup, and endpoint connection queries.

## Important APIs, Types, And Functions
Exported APIs include `dprc_open()`, `dprc_close()`, `dprc_reset_container()`, IRQ functions (`dprc_set_irq()`, `dprc_set_irq_enable()`, `dprc_set_irq_mask()`, `dprc_get_irq_status()`, `dprc_clear_irq_status()`), inventory functions (`dprc_get_attributes()`, `dprc_get_obj_count()`, `dprc_get_obj()`, `dprc_get_obj_region()`), `dprc_get_api_version()`, `dprc_get_container_id()`, and `dprc_get_connection()`. The file caches DPRC API major/minor versions in static variables to select command variants.

## Control Flow
Each API constructs an MC command, fills command-specific parameters, sends it with `mc_send_command()`, and decodes response fields. Version-aware calls choose newer command IDs for reset options and object regions: reset uses V2 for API >= 6.5, and region lookup uses V2/V3 for API >= 6.3/6.6 so base address and 64K portal sizing are represented correctly.

## State And Persistence
The only local state is cached DPRC API version. MC firmware owns all container, interrupt, object, region, and connection state. Callers hold tokens returned from open operations.

## Dependencies And Integration Points
This is the command-marshaling layer beneath `dprc-driver.c` and other fsl-mc components. It depends on private command IDs/parameter structures, endian helpers, MC portal I/O, and public fsl-mc descriptors.

## Risks And Test Signals
Risks include firmware API drift, stale global version cache across heterogeneous portals, endian/layout mismatches, returning `-ENOTCONN` for all connection query errors, and incorrect region sizing on older MC versions. Test signals are MC command conformance tests, object scan correctness, IRQ programming success, child container reset behavior for different API versions, and endpoint connection discovery.
