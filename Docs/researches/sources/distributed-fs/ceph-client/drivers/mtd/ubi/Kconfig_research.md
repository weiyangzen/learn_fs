# sources/distributed-fs/ceph-client/drivers/mtd/ubi/Kconfig

## Purpose
Defines kernel configuration options for UBI, the MTD layer that provides logical volumes, wear leveling, bad-block handling, optional fast attach, block-device export, fault injection, gluebi, and NVMEM exposure.

## Important APIs, Types, and Functions
The root option is `MTD_UBI`, a tristate that selects `CRC32`. Suboptions include `MTD_UBI_WL_THRESHOLD`, `MTD_UBI_BEB_LIMIT`, `MTD_UBI_FASTMAP`, `MTD_UBI_GLUEBI`, `MTD_UBI_BLOCK`, `MTD_UBI_FAULT_INJECTION`, and `MTD_UBI_NVMEM`.

## Control Flow
Kconfig gates all suboptions under `if MTD_UBI`. Defaults favor conservative behavior: Fastmap, block, fault injection, and NVMEM are disabled by default; wear leveling threshold defaults to 4096; expected bad eraseblocks defaults to 20 per 1024.

## State and Persistence
Configuration choices become build-time state and influence runtime UBI policy, including reserved PEB calculations, wear-leveling behavior, and compiled feature availability. Fastmap has on-flash format implications.

## Dependencies and Integration Points
UBI depends on MTD and CRC32. `MTD_UBI_BLOCK` depends on `BLOCK`, fault injection depends on `FAULT_INJECTION_DEBUG_FS`, and NVMEM support depends on `NVMEM`.

## Risks
Bad tuning can reserve too few PEBs or wear-level too aggressively/weakly. Fastmap is marked experimental and can affect attach behavior and on-flash metadata. Enabling gluebi or block devices exposes additional interfaces over UBI volumes.

## Test Signals
Build matrix tests should cover UBI as built-in/module, with and without Fastmap/block/gluebi/nvmem. Runtime tests should verify attach, wear-leveling policy, bad-block reservation, and option-specific devices.
