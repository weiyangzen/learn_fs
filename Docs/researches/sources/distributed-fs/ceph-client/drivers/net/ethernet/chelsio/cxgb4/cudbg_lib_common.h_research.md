# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib_common.h

## Purpose
This header defines common CUDBG dump headers, entity headers, buffer/error structures, compression constants, and common buffer helper prototypes.

## Important APIs, Types, And Functions
- `struct cudbg_hdr` is the top-level dump header with signature, version, total data length, entity count, chip version, dump type, and compression type.
- `struct cudbg_entity_hdr` describes each entity's type, start offset, size, error/warning fields, padding, and extension metadata.
- `struct cudbg_ver_hdr` versions selected entity payloads.
- `struct cudbg_buffer` and `struct cudbg_error` are the common collection data/error carriers.
- `CDUMP_MAX_COMP_BUF_SIZE` and `CUDBG_CHUNK_SIZE` define compression chunk sizing.

## Control Flow
There is no executable flow here. The structure definitions drive `cxgb4_cudbg_collect()` header initialization, per-entity collection, alignment, and error propagation.

## State And Persistence
Instances of `cudbg_hdr`, `cudbg_entity_hdr`, and versioned payload headers are serialized into ethtool/vmcore dumps. `cudbg_buffer` and `cudbg_error` are transient in-kernel structures.

## Dependencies And Integration Points
It depends on `struct cudbg_init` being declared by `cudbg_if.h` before the helper prototypes are used. It is included by `cudbg_common.c`, `cudbg_lib.c`, `cudbg_zlib.c`, and `cxgb4_cudbg.c`.

## Risks
Changing header layout or constants can break userspace decoders. Entity headers are indexed by entity ID minus one, so `max_entities` and enum values must remain compatible. Compression chunk size affects maximum temporary buffer requirements and output format.

## Test Signals
Dump-header parser tests, entity-offset/padding validation, compression and no-compression collection tests, and compatibility checks against existing CUDBG decoder tools.
