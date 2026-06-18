<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/zns.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/zns.c

## Purpose
Implements NVMe Zoned Namespace host support: discovers ZNS limits, configures block queue zoned limits, reports zones to the block layer, and builds zone management send commands.

## Important APIs, Types, And Functions
Key exported helpers are `nvme_query_zone_info()`, `nvme_update_zone_info()`, `nvme_ns_report_zones()`, and `nvme_setup_zone_mgmt_send()`. Internal helpers include `nvme_set_max_append()`, `nvme_zns_alloc_report_buffer()`, and `nvme_zone_parse_entry()`. It works with `struct nvme_zone_info`, ZNS identify data, `struct queue_limits`, and block-layer `struct blk_report_zones_args`.

## Control Flow
Namespace scan calls `nvme_query_zone_info()`, which checks command effects for zone append support, lazily identifies controller ZNS append size, identifies namespace ZNS data, rejects unsupported zone operation characteristics, validates power-of-two zone size, and records max open/active zones. `nvme_update_zone_info()` transfers that data to queue limits. Zone reporting allocates a bounded vmalloc report buffer, issues repeated zone management receive commands starting at zone-aligned sectors, converts each NVMe descriptor to `struct blk_zone`, and advances until the requested count or disk capacity is reached. Zone reset/open/close/etc. requests are encoded by `nvme_setup_zone_mgmt_send()`.

## State And Persistence
Persistent runtime state is stored in `ctrl->max_zone_append`, `ns->head->zsze`, queue limits, and the namespace force-read-only flag. Report buffers and identify data are temporary allocations.

## Dependencies And Integration Points
Depends on NVMe admin identify and sync command submission, NVMe command effects logs, block zoned queue limits, gendisk zone reporting, and helpers converting between LBAs and sectors. It gates writable zoned namespace behavior on zone append command support.

## Risks
Incorrect zone-size validation or sector/LBA conversion would corrupt block-layer zone geometry. Devices without zone append are forced read-only, so command effects log accuracy matters. Report buffer sizing must stay within queue segment and hardware-sector limits. NVMe positive status codes from report commands are normalized to `-EIO`.

## Test Signals
Test ZNS namespaces with and without zone append, invalid non-power-of-two zone sizes, max append limits with and without `zasl`, report-zones over partial and full disk ranges, full-zone write pointer handling, and all block zone management request mappings. Compare `blkzone report` output with raw NVMe zone reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/zns.c -->
