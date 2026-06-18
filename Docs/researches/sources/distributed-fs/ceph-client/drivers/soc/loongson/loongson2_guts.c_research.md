
# sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_guts.c

## Purpose
Loongson-2 Global Utilities (GUTS) register-block driver. It maps chip ID registers, reads SVR, matches known die IDs, and registers SoC bus identity attributes.

## Important APIs, Types, and Functions
- `struct scfg_guts` models selected global utility registers.
- Static global `guts` stores register base and endianness.
- `loongson2_guts_get_svr()` reads SVR with configured endianness.
- `loongson2_guts_probe()` maps registers and registers `soc_device`.
- `loongson2_guts_init()` registers the platform driver at `core_initcall()`.

## Control Flow
Probe allocates global guts state, reads `little-endian`, maps resource 0, reads root model or compatible as machine, reads SVR, matches die table, formats family/soc_id/revision strings, registers the SoC device, and logs identity. Remove unregisters the global SoC device.

## State and Persistence
Global static `soc_dev_attr`, `soc_dev`, and `guts` persist while bound. Hardware SVR is read-only identity state. No file persistence.

## Dependencies and Integration Points
Depends on OF platform resources, root DT model/compatible, SoC bus core, and compatible `loongson,ls2k-chipid`.

## Risks
- Global singleton state assumes one device instance.
- If root node lookup fails, dereferencing/using `machine` assumptions could be fragile; normal DT has root.
- Only one die match is currently known; unknown chips register generic Loongson family.

## Test Signals
Probe with little/big endian SVR, known and unknown die values, missing root model fallback to compatible, SoC bus registration failure, and remove unregister.
