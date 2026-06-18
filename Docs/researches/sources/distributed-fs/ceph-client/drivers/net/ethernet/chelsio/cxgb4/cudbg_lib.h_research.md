# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.h

## Purpose
This header declares the CUDBG collector API implemented by `cudbg_lib.c` and provides inline helpers for mapping cxgb4 queue types into CUDBG qdesc entries.

## Important APIs, Types, And Functions
It declares every `cudbg_collect_*()` function used by `cxgb4_cudbg.c`, plus sizing and helper functions such as `cudbg_get_entity_length()`, `cudbg_get_entity_hdr()`, `cudbg_align_debug_buffer()`, `cudbg_cim_obq_size()`, `cudbg_dump_context_size()`, `cudbg_fill_meminfo()`, `cudbg_fill_le_tcam_info()`, and `cudbg_fill_qdesc_num_and_size()`. Inline helpers map ULD TX/RX/FL/CI queues to `enum cudbg_qdesc_qtype` and copy TX, RX, and freelist descriptors into a `cudbg_qdesc_entry`.

## Control Flow
The header has no standalone flow. Its inline qdesc helpers are invoked by `cudbg_collect_qdesc()` to populate descriptor metadata and data, then advance via `cudbg_next_qdesc()`.

## State And Persistence
The header defines access patterns for snapshotting live queue descriptor rings. It does not allocate or persist state itself. The copied descriptor bytes become persistent only inside the generated CUDBG dump.

## Dependencies And Integration Points
It depends on CUDBG entity definitions, cxgb4 queue structures (`sge_txq`, `sge_rspq`, `sge_fl`), and constants for ULD IDs. It is included by `cxgb4_cudbg.h` so the ethtool/vmcore glue can see collector prototypes and callback types.

## Risks
The qdesc helpers blindly `memcpy()` descriptor memory based on queue size and descriptor size, so callers must ensure queues are initialized and buffers are sized. Unknown ULD IDs map to `CUDBG_QTYPE_UNKNOWN`, which may reduce decoder usefulness. Prototype drift between this header and `cudbg_lib.c` will break builds.

## Test Signals
Compile tests across optional ULD feature configs, CUDBG collection with NIC/ULD/ETHOFLD queues present and absent, and decoder checks for qdesc entry sizing/order are relevant.
