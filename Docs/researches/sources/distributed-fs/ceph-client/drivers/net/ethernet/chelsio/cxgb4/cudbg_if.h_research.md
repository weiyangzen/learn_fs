# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_if.h

## Purpose
This header defines the public CUDBG collection interface: status codes, dump version, entity IDs, initialization context, and a size conversion helper.

## Important APIs, Types, And Functions
- Status codes include `CUDBG_STATUS_NO_MEM`, `CUDBG_STATUS_ENTITY_NOT_FOUND`, `CUDBG_STATUS_NOT_IMPLEMENTED`, `CUDBG_SYSTEM_ERROR`, `CUDBG_STATUS_CCLK_NOT_DEFINED`, and `CUDBG_STATUS_PARTIAL_DATA`.
- `enum cudbg_dbg_entity_type` assigns stable IDs for all dump entities from register dumps through flash.
- `struct cudbg_init` passes the adapter, output buffer, compression mode, compression buffer, and zlib workspace to collectors.
- `cudbg_mbytes_to_bytes()` converts hardware memory-size units to bytes.

## Control Flow
There is no executable control flow except the inline conversion helper. The enum values drive `cxgb4_cudbg.c` entity arrays, `cudbg_get_entity_hdr()` indexing, and `cudbg_get_entity_length()` sizing.

## State And Persistence
`struct cudbg_init` is per-collection transient state. The major/minor version (`1.14`) is written into `struct cudbg_hdr` and persists in generated dumps for decoder compatibility.

## Dependencies And Integration Points
The file depends on `struct adapter` being visible through includers. It is included by CUDBG common, zlib, library, and cxgb4 glue files. Entity IDs must remain synchronized with collector tables and userspace dump decoders.

## Risks
Changing entity numeric values or versioning without decoder coordination breaks compatibility. The helper uses integer multiplication; very large memory-size units would overflow `unsigned int`, though hardware values are expected to fit the driver dump model.

## Test Signals
Compile coverage for all CUDBG translation units, decoder compatibility against version `1.14`, and entity table tests verifying every collected entity has a matching length and header slot.
