# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.h

## Purpose
This header defines cxgb4-specific CUDBG glue: dump buffer sizes, callback type, entity/callback mapping structure, ethtool dump flag bits, and public cxgb4 CUDBG entry points.

## Important APIs, Types, And Functions
- `CUDBG_DUMP_BUFF_SIZE` is the 32 MB capped dump buffer used for compressed and vmcore scenarios.
- `CUDBG_COMPRESS_BUFF_SIZE` is the 4 MB reusable input buffer for compression.
- `cudbg_collect_callback_t` is the collector callback signature.
- `struct cxgb4_collect_entity` pairs `enum cudbg_dbg_entity_type` with a collector callback.
- `enum CXGB4_ETHTOOL_DUMP_FLAGS` defines memory, hardware, flash, and all-dump selections.
- Prototypes expose dump length, collection, ethtool initialization, and vmcore registration.

## Control Flow
The header has no executable flow. Its types are consumed by `cxgb4_cudbg.c` to build static entity arrays and dispatch collectors.

## State And Persistence
No state is stored here. The constants determine allocation sizes and serialized dump availability. Flags persist in `adapter->eth_dump.flag` when ethtool dump configuration is stored.

## Dependencies And Integration Points
It includes CUDBG interface/common/entity/library headers and depends on Linux ethtool dump flag definitions through cxgb4 include context. It is the boundary between generic CUDBG collector code and cxgb4 ethtool/vmcore integration.

## Risks
Changing buffer constants affects memory pressure and truncation behavior. Adding a new dump flag requires matching length and collection logic. The `CXGB4_ETH_DUMP_ALL` macro excludes flash by design, so callers expecting full flash data must request `CXGB4_ETH_DUMP_FLASH` separately.

## Test Signals
Compile tests, dump flag combination tests, memory allocation behavior around 32 MB/4 MB limits, and vmcore dump sizing checks.
