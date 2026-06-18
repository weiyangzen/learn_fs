<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi_endian.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/cfi_endian.h

## Purpose
`mtd/cfi_endian.h` defines byte-order conversion helpers for CFI flash access based on map swap policy.

## Important APIs, Types, and Functions
It defines `CFI_HOST_ENDIAN`, `CFI_LITTLE_ENDIAN`, `CFI_BIG_ENDIAN`, `CFI_DEFAULT_ENDIAN`, `cfi_default()`, `cfi_be()`, `cfi_le()`, `cfi_host()`, `cpu_to_cfi8/16/32/64()`, `cfi8/16/32/64_to_cpu()`, and internal `_cpu_to_cfi()`, `_cfi_to_cpu()`, `_swap_to_cfi()`, `_swap_to_cpu()` macros.

## Control Flow and State
CFI map code sets or leaves `map->swap`; conversion macros either pass values through for host endian or call CPU endian conversion macros for big/little CFI byte order.

## State and Persistence Behavior
No state is owned. It interprets `map_info::swap` and Kconfig defaults.

## Dependencies and Integration Points
It depends on architecture byteorder helpers and CFI map drivers. It is included by `cfi.h`.

## Risks
Wrong default endian selection or map swap value corrupts command/query interpretation. The file intentionally has no include guard, so repeated inclusion must be harmless.

## Test Signals
CFI probe on big-endian/little-endian systems, map swap option tests, read/write query values, and config coverage for NOSWAP/LE/BE advanced options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi_endian.h -->
