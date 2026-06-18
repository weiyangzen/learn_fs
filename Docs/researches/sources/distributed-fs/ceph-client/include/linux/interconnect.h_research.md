<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect.h -->
# sources/distributed-fs/ceph-client/include/linux/interconnect.h

Purpose: Defines consumer-side Linux interconnect APIs for acquiring paths and setting bandwidth constraints.

Important APIs/types/functions: Unit conversion macros convert Bps/kBps/MBps/GBps and bit rates into ICC units. `ICC_ALLOC_DYN_ID` requests dynamic node ids. `struct icc_bulk_data` stores path, firmware name, average bandwidth, and peak bandwidth. APIs get/put paths by name or index, devm/bulk get paths, enable/disable paths, set bandwidth and tags, get names, and bulk set/enable/disable/put. Disabled builds return NULL or success no-ops.

Control flow: Consumer drivers acquire paths at probe, set avg/peak bandwidth around runtime needs, enable/disable paths with device activity, and release paths on remove.

State/persistence: `icc_path` state is opaque and persists from get to put; bulk data stores desired bandwidths.

Dependencies/integration: Integrates device tree interconnect properties, runtime PM, provider aggregation, and Kconfig stubs.

Risks: Disabled-config no-ops can hide missing bandwidth votes; unit conversions intentionally use kBps-like ICC units and need caller care.

Test signals: Named/indexed path lookup, bandwidth vote aggregation, bulk APIs, enable/disable ordering, provider-disabled no-op behavior, and DT property errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect.h -->
