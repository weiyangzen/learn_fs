# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_hwconfig.c

## Purpose
Obtains, stores, copies, dumps, and searches the GuC hardware configuration table.

## Important APIs, Types, And Functions
Exports `xe_guc_hwconfig_init`, `xe_guc_hwconfig_size`, `xe_guc_hwconfig_copy`, `xe_guc_hwconfig_dump`, and `xe_guc_hwconfig_lookup_u32`. Internal helpers send `XE_GUC_ACTION_GET_HWCONFIG` first to query size and then to copy the table into a GGTT BO.

## Control Flow
Initialization is idempotent, runs only on GT0, and only on ADL-P or graphics version 12.55 and newer. It queries size, rejects zero size, allocates a managed pinned/mapped system GGTT BO, stores it in `guc->hwconfig`, and asks GuC to copy the table into it. Dump and lookup allocate temporary host memory, copy from the BO mapping, then iterate key-length-value entries.

## State And Persistence
Persistent state is `guc->hwconfig.bo` and `guc->hwconfig.size`, managed for the device lifetime. The table is copied once and then read through mapped BO memory.

## Dependencies And Integration Points
Depends on GuC MMIO send, GuC action ABI, Xe BO/pin/map helpers, GT/tile/device metadata, and DRM printer APIs. Consumers use the size/copy/lookup APIs for platform feature data.

## Risks And Test Signals
The KLV-style parser checks for truncated entries during dumps but `lookup_u32` assumes the matched key has at least one value dword. Initialization is platform-gated; test signals include successful table size query, nonzero size, dump output without truncation errors, and expected attribute lookup results.
