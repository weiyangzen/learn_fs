<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-efuses.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/apple-efuses.c

## Purpose
Registers memory-mapped Apple SoC eFuses as a root-only, read-only NVMEM provider with legacy fixed OF cell support.

## Important APIs, Types, And Functions
`struct apple_efuses_priv` stores the ioremapped fuse base. `apple_efuses_read()` reads 32-bit words with `readl_relaxed()`. `apple_efuses_probe()` maps the platform resource, sizes the provider from the resource, and registers `apple_efuses_nvmem` with automatic ids.

## Control Flow
OF match on `apple,efuses` triggers probe. Probe allocates private state, maps resource 0, fills config, and calls `devm_nvmem_register()`. Read callbacks iterate word-by-word from the requested offset.

## State And Persistence
Only the MMIO base is kept in driver memory. Fuse data persists in hardware and the provider is read-only and root-only.

## Dependencies And Integration Points
Depends on platform resources, OF match, MMIO accessors, and NVMEM fixed OF cell parsing. Consumers such as PHY or board drivers can retrieve calibration data through NVMEM cells.

## Risks
The read path ignores trailing byte counts smaller than 32 bits, relying on core word-size alignment. Root-only access is important because fuses may contain sensitive identifiers. Relaxed reads assume no special sequencing is needed.

## Test Signals
Boot on matching Apple SoC DT, verify resource size maps to NVMEM size, read fixed cells, confirm unprivileged sysfs restrictions, and check no partial-word reads are attempted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/apple-efuses.c -->
