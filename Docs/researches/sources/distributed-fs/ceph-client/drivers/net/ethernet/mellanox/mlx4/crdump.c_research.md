# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/crdump.c

## Purpose
This file collects mlx4 firmware crash dumps into devlink regions. It snapshots PCI CR space and the firmware health buffer when crash dumping is enabled and supported.

## Important APIs and Functions
- `mlx4_crdump_init()` creates devlink regions `cr-space` and `fw-health`.
- `mlx4_crdump_collect()` maps PCI BAR0, obtains a devlink snapshot id, enables CR-space access, collects both regions, restores access state, and unmaps.
- `mlx4_crdump_collect_crspace()` copies BAR0 CR space into a vmalloc buffer and creates a devlink snapshot.
- `mlx4_crdump_collect_fw_health()` snapshots the health buffer.
- `mlx4_crdump_end()` destroys devlink regions.

## Control Flow
Collection is skipped if firmware lacks a health buffer address or snapshots are disabled. Otherwise, BAR0 is mapped, volatile CR access is blocked, the firmware CR filter is temporarily relaxed, region snapshots are created, and all access bits are restored before unmapping.

## State and Persistence
`dev->persist->crdump` stores devlink region pointers and the `snapshot_enable` flag. Snapshot data persists in devlink until consumed or evicted by the region's snapshot limit. A static boolean tracks whether the CR enable bit was set before dumping.

## Dependencies and Integration Points
It integrates with devlink regions/snapshots, PCI BAR resources, firmware health buffer capabilities, and catastrophic error recovery in `catas.c`.

## Risks and Test Signals
Risks include large BAR allocation failure, failure to restore CR filter state, static CR enable state shared across devices, and snapshot create failures leaking diagnostic coverage. Test signals include devlink region visibility, snapshot creation after injected firmware error, disabled snapshot behavior, and allocation failure logging.
