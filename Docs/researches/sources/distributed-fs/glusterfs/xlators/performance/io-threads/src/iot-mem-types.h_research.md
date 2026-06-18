# sources/distributed-fs/glusterfs/xlators/performance/io-threads/src/iot-mem-types.h

## Purpose
Defines io-threads-specific memory accounting type IDs.

## Important APIs, types, and functions
`enum gf_iot_mem_types_` defines allocation classes for `iot_conf_t` and client queue context arrays, ending at `gf_iot_mt_end`.

## Control flow
No control flow exists. `mem_acct_init()` registers the enum range, and allocation sites use the IDs for diagnostics.

## State and persistence behavior
The enum affects runtime memory accounting only. It is not persisted.

## Dependencies and integration points
Depends on `glusterfs/mem-types.h` and integrates with xlator memory accounting.

## Risks and test signals
Risks are enum overlap, missing new allocation classes, and confusing memory leak attribution. Test signals include successful memory accounting init and statedump/leak reports showing io-threads allocations under the right categories.
