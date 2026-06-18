# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.c

## Purpose
This file is the cxgb4 integration layer for CUDBG collection. It selects which CUDBG entities belong to hardware, memory, and flash dumps; computes dump lengths; initializes CUDBG headers; runs collectors; enables optional compression; and registers vmcore device dumps.

## Important APIs, Types, And Functions
- `cxgb4_collect_hw_dump`, `cxgb4_collect_mem_dump`, and `cxgb4_collect_flash_dump` map entity IDs to collector callbacks.
- `cxgb4_get_dump_length()` sums entity lengths and caps large compressed dumps to `CUDBG_DUMP_BUFF_SIZE`.
- `cxgb4_cudbg_collect_entity()` iterates entity arrays, fills entity headers, invokes collectors, aligns buffers, and records errors/warnings.
- `cxgb4_cudbg_collect()` builds the top-level CUDBG header and performs selected HW/MEM/FLASH collection.
- `cxgb4_init_ethtool_dump()` initializes `adapter->eth_dump`.
- `cxgb4_cudbg_vmcore_add_dump()` registers a crash dump callback.

## Control Flow
Collection starts with caller-supplied buffer size and flags. The function writes `cudbg_hdr`, validates minimum space for all entity headers, probes zlib workspace availability, allocates compression buffers when possible, then advances the data offset past the header table. Each selected group is collected in order. Per-entity failures reset the data offset to the entity start and preserve failure status in the entity header, allowing later entities to continue.

## State And Persistence
Persistent driver state touched here is `adapter->eth_dump` and `adapter->vmcoredd`. Dump contents persist in the caller-provided buffer. Compression scratch state is allocated per collection and freed before return. Entity errors are persisted in `cudbg_entity_hdr`.

## Dependencies And Integration Points
It depends on `t4_regs.h`, `cxgb4.h`, `cxgb4_cudbg.h`, and `cudbg_zlib.h`. It integrates with ethtool dump operations through `eth_dump` fields and with kdump/vmcore through `vmcore_add_device_dump()`.

## Risks
`cudbg_free_compress_buff()` is called unconditionally even when compression allocation was skipped; `vfree(NULL)` is safe, but any future allocator change must preserve that. Buffer length estimates must match collector behavior, especially when compression caps output. Continuing after entity failure is intentional, but consumers must inspect per-entity `hdr_flags`, `sys_err`, and `sys_warn`.

## Test Signals
Collect dumps for each flag combination, with too-small buffers, zlib allocation failure, collector failure injection, and vmcore registration. Verify header versions, entity offsets/sizes/padding, compressed versus uncompressed final `buf_size`, and ethtool `eth_dump` initialization.
