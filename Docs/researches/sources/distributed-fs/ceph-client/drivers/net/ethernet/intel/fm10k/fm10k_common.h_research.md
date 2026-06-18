# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_common.h

## Purpose
`fm10k_common.h` declares fm10k generic hardware helpers and provides guarded MMIO write macros shared by PF/VF/common code.

## Important APIs, types, and functions
It declares PCI config and register reads, generic bus/invariant/start/stop/stats/host-state functions, and defines `FM10K_REMOVED`, `fm10k_write_reg`, `fm10k_write_sw_reg`, `fm10k_write_flush`, `fm10k_update_hw_base_32b`, and `fm10k_unbind_hw_stats_32b`.

## Control flow
The write macros use `READ_ONCE` on `hw->hw_addr` or `hw->sw_addr`, skip writes when the device mapping has been removed, and issue `writel` to DWORD-indexed register arrays. `fm10k_write_flush` performs a safe control-register read to flush prior posted writes.

## State and persistence behavior
The macros mutate device MMIO state but do not store state themselves. The helper macros update stat base fields in memory. Removed-device detection is a persistent safety convention used throughout the driver after surprise removal or teardown.

## Dependencies and integration points
The header includes `fm10k_type.h` for hardware structures and register constants. It is included by `fm10k_common.c` and lower-level PF/VF code that needs safe MMIO access.

## Risks
The register index unit is DWORDS, not bytes; passing byte offsets would write the wrong registers. `FM10K_REMOVED` only checks pointer presence, not device health. The 32-bit stat base macro assumes caller has already computed a valid delta.

## Test signals
Build coverage, hot-unplug/surprise-removal tests, queue start/stop flush behavior, and statistics consistency validate this header's contracts.
