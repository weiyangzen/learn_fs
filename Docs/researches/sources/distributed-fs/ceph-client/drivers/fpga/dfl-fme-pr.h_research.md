## sources/distributed-fs/ceph-client/drivers/fpga/dfl-fme-pr.h

Purpose: this header defines platform data and list node structures shared by FME partial-reconfiguration orchestration, manager, bridge, and region child drivers.

Important types and APIs: `struct dfl_fme_region` links a region platform device to a port ID. `struct dfl_fme_region_pdata` passes the manager and bridge platform devices to the region driver and reserves a `region_id` field. `struct dfl_fme_bridge` tracks bridge platform devices in the FME list. `struct dfl_fme_br_pdata` passes the DFL container and port ID to bridge devices. `struct dfl_fme_mgr_pdata` passes the PR MMIO address to the manager. String macros define platform driver names for manager, bridge, and region.

Control flow and integration: `dfl-fme-pr.c` creates platform devices using these payloads. `dfl-fme-mgr.c`, `dfl-fme-br.c`, and `dfl-fme-region.c` consume the payloads during probe. The names are also used as module aliases and Kconfig-selected driver identities.

State and persistence: the structures define runtime topology rather than hardware state. They persist for the lifetime of child platform devices and connect a single FME manager to multiple port-specific bridge/region pairs.

Dependencies and risks: it depends on platform-device declarations and DFL container types via included headers in consumers. The `region_id` field is documented but not set by current region creation, so consumers should not rely on it unless fixed. Lifetime is tied to platform device data copies and devm allocations in the creator.

Test signals: compile child drivers independently, verify platform data sizes and copies, check module aliases match macros, and validate region/bridge topology for each implemented port.
