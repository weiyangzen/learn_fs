# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.c

## Purpose
This file is the main cxgb4 CUDBG collector library. It calculates entity sizes and implements collectors for registers, firmware logs, CIM queues and logic analyzers, adapter memories, RSS, PM/hardware scheduler stats, indirect register banks, SGE contexts, MPS/LE TCAMs, VPD, mailbox logs, queue descriptors, flash, and T6-specific blocks.

## Important APIs, Types, And Functions
- `cudbg_get_entity_length()` returns the expected payload size for each entity based on chip version, firmware parameters, memory BARs, queue sizes, and software state.
- Buffer helpers `cudbg_do_compression()`, `cudbg_write_and_release_buff()`, `cudbg_align_debug_buffer()`, and `cudbg_get_entity_hdr()` support the collection framework.
- `cudbg_fill_meminfo()`, memory-region helpers, `cudbg_memory_read()`, and `cudbg_read_fw_mem()` map and read EDC/MC/HMA memory while skipping large Tx/Rx payload regions.
- Collector families include `cudbg_collect_cim_*`, `cudbg_collect_*_meminfo`, `cudbg_collect_*_indirect`, `cudbg_collect_dump_context()`, `cudbg_collect_mps_tcam()`, `cudbg_collect_le_tcam()`, `cudbg_collect_qdesc()`, and `cudbg_collect_flash()`.

## Control Flow
The top-level caller in `cxgb4_cudbg.c` selects an entity and calls the matching function. Most collectors allocate a temporary CUDBG buffer, fill it via `t4_*` hardware/firmware helpers, set `cudbg_err` on failures, then write/release the buffer with optional chunked compression. Memory dumps first build a memory map, flush firmware cache when available, then read in `CUDBG_CHUNK_SIZE` chunks and periodically `schedule()` to avoid CPU-stall warnings. Context dumps prefer firmware reads/flushes, but fall back to backdoor register access. TCAM collectors read every table index and use firmware mailbox reads for replicate maps when possible, falling back to direct registers.

## State And Persistence
The library does not own long-lived state. It snapshots `struct adapter` fields, mailbox logs, SGE queues, ULD queue arrays, firmware memory, flash, and hardware registers into the caller-provided dump buffer. It uses locks for shared state: `win0_lock` for memory windows, `uld_mutex` for ULD queues, and `tc_mqprio->mqprio_mutex` for ETHOFLD queue descriptors.

## Dependencies And Integration Points
It depends heavily on `cxgb4.h`, `t4_regs.h`, firmware APIs, CUDBG headers, zlib wrapper, Linux `sort`, allocation, mutex, and scheduling primitives. It integrates with ethtool dump and vmcore dump through `cxgb4_cudbg.c`. It also depends on hardware generation helpers (`is_t4/t5/t6`, `CHELSIO_CHIP_VERSION`) to choose register arrays and memory semantics.

## Risks
Entity length and actual collector output must stay aligned; mismatches can truncate or leave unused space. Many collectors read live hardware and may perturb state or race with traffic; `cudbg_collect_sge_indirect()` intentionally avoids certain T6 registers while ports are running. Partial-data handling varies between collectors. `cudbg_collect_qdesc()` reserves a worst-case buffer capped to `CUDBG_DUMP_BUFF_SIZE`, so large live queue sets can yield partial output. Memory-window reads require alignment and locking; bad region math can read wrong adapter memory.

## Test Signals
Validation should collect dumps on T4, T5, and T6 with compression enabled/disabled, ports idle/running, firmware attached/unattached, and large memory/flash sizes. Decoder tests should verify all entity headers, sizes, padding, partial-data warnings, qdesc counts, TCAM/TID boundaries, and memory-map regions. Fault injection for mailbox, PCI config, VPD, flash, and memory reads is useful.
