# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_fusion.h

## Purpose

`megaraid_sas_fusion.h` defines the Fusion controller ABI and in-driver data structures used by `megaraid_sas_fusion.c`, `megaraid_sas_fp.c`, and the common MegaRAID SAS code. It describes MPI2/MegaRAID request and reply frames, RAID context layouts for pre-Ventura and Ventura/G35 controllers, RAID map layouts from firmware, driver-normalized map layouts, SGL/PRP structures, task-management frames, load-balance and uneven-span caches, command objects, and the `fusion_context` that owns Fusion runtime resources.

This header is the contract that makes the driver command path and map path agree on field offsets, endian types, bit masks, and controller feature flags. Many structures directly mirror firmware DMA formats, so layout stability and endian correctness are central.

## Important Types And Constants

Core controller constants include `MEGA_MPI2_RAID_DEFAULT_IO_FRAME_SIZE`, `MEGASAS_MPI2_FUNCTION_PASSTHRU_IO_REQUEST`, `MEGASAS_MPI2_FUNCTION_LD_IO_REQUEST`, `MFI_FUSION_ENABLE_INTERRUPT_MASK`, `MEGASAS_FUSION_MAX_RESET_TRIES`, `MAX_MSIX_QUEUES_FUSION`, RDPQ chunk sizing, reset bits, and chain-frame sizing masks. Request descriptor flags define LD I/O, MFA passthrough, no-lock, fast-path I/O, high-priority, and SCSI I/O descriptor types.

`struct RAID_CONTEXT` is the older MegaRAID-specific I/O context placed where SGLs would normally begin in the MPT frame. It carries timeout, region-lock flags, virtual disk target id, row LBA, lock length, firmware status, RAID flags, SGE counts, config sequence, span/arm, and priority.

`struct RAID_CONTEXT_G35` is the Ventura/G35 layout. It replaces several byte fields with `nseg_type`, `routing_flags`, and a `flow_specific` union used for RAID5/6 RMW indices, RAID1 peer SMIDs, or R5/6 arm maps. It also packs stream-detected and SGE-count bits in a union. Inline helpers `set_num_sge()`, `get_num_sge()`, and `is_stream_detected()` manipulate this format.

`union RAID_CONTEXT_UNION` lets request frames expose either RAID context layout at the same offset. Span/arm and RAID5/6 arm-map masks define how physical arm and span are packed into firmware-visible fields.

MPI2 and SGL definitions include `MPI25_IEEE_SGE_CHAIN64`, `MPI2_SGE_SIMPLE_UNION`, `MPI2_SGE_CHAIN_UNION`, IEEE simple/chain SGE formats, `union MPI2_SGE_IO_UNION`, `union MPI2_SCSI_IO_CDB_UNION`, `MPI2_RAID_SCSI_IO_REQUEST`, `MPI2_IOC_INIT_REQUEST`, and PRP/NVMe SGE flag constants. These are used for normal SGLs, chained SGLs, NVMe PRP lists, IOC init, and T10 PI/EEDP CDB embedding.

Request/reply descriptor types include `union MEGASAS_REQUEST_DESCRIPTOR_UNION` and `union MPI2_REPLY_DESCRIPTORS_UNION`, with variants for default, high-priority, SCSI I/O, target, RAID accelerator, and MFA descriptors. `union desc_value` and `union desc_word` are convenience views for low/high descriptor words.

Task management structures include `MPI2_SCSI_TASK_MANAGE_REQUEST`, `MPI2_SCSI_TASK_MANAGE_REPLY`, `MR_TASK_MANAGE_REQUEST`, `MR_TM_REQUEST`, `MR_TM_REPLY`, task type constants, and response-code constants. They support abort task and target reset paths in the Fusion implementation.

RAID map structures include `MR_DEV_HANDLE_INFO`, `MR_ARRAY_INFO`, `MR_QUAD_ELEMENT`, `MR_SPAN_INFO`, `MR_LD_SPAN`, `MR_SPAN_BLOCK_INFO`, `MR_CPU_AFFINITY_MASK`, `MR_IO_AFFINITY`, `MR_LD_RAID`, `MR_LD_SPAN_MAP`, `MR_FW_RAID_MAP`, `MR_FW_RAID_MAP_ALL`, `MR_FW_RAID_MAP_EXT`, `MR_FW_RAID_MAP_DYNAMIC`, `MR_RAID_MAP_DESC_TABLE`, `MR_DRV_RAID_MAP`, and `MR_DRV_RAID_MAP_ALL`. These describe firmware legacy, extended, and dynamic map formats plus the normalized driver-side map. Static assertions verify flexible-array overlap offsets for the wrapped layouts.

Runtime helper state includes `struct IO_REQUEST_INFO` for per-I/O geometry and fast-path decisions, `struct megasas_cmd_fusion` for one Fusion command, `struct LD_LOAD_BALANCE_INFO` for RAID1 mirror selection, `LD_SPAN_SET`/`LD_SPAN_INFO` for uneven-span derived ranges, `STREAM_DETECT`/`LD_STREAM_DETECT` for sequential I/O hints, `rdpq_alloc_detail` for reply queue chunk ownership, `MR_PD_CFG_SEQ` and `MR_PD_CFG_SEQ_NUM_SYNC` for JBOD sequence maps, and `struct fusion_context` for all Fusion resources attached to an adapter.

Public prototypes at the end expose Fusion lifecycle and map functions: `megasas_free_cmds_fusion()`, `megasas_ioc_init_fusion()`, `megasas_get_map_info()`, `megasas_sync_map_info()`, `megasas_release_fusion()`, `megasas_reset_reply_desc()`, `megasas_check_mpio_paths()`, and `megasas_fusion_ocr_wq()`.

## Control Flow And Integration

The command path allocates one `megasas_cmd_fusion` per MPT/Fusion command. Each command points to a DMA-backed `MPI2_RAID_SCSI_IO_REQUEST`, optional chain frame, sense buffer, request descriptor, associated SCSI command, and sync-command index for tunneled MFI commands. `fusion_context->cmd_list` maps SMID/tag indexes to these command objects, and completion uses reply SMID values to recover the command.

The I/O frame layout is centered on `struct MPI2_RAID_SCSI_IO_REQUEST`: devhandle, function, sense address, SGL flags, data length, CDB, RAID context union, and SGL storage. `megaraid_sas_fusion.c` fills this structure and posts a `MEGASAS_REQUEST_DESCRIPTOR_UNION` to the inbound queue. Firmware writes completion information into the RAID context and posts a `MPI2_REPLY_DESCRIPTORS_UNION` entry.

The map path uses firmware layouts as DMA inputs and `MR_DRV_RAID_MAP_ALL` as the normalized output. `megaraid_sas_fp.c` consumes `MR_LD_RAID`, `MR_LD_SPAN_MAP`, `MR_ARRAY_INFO`, and `MR_DEV_HANDLE_INFO` to calculate fast-path placement. Dynamic maps use descriptor tables to locate the arrays inside a variable-size firmware buffer.

The reset path uses constants and structures from this header to reset descriptors (`ULLONG_MAX` unused markers), refill IOC init fields, rebuild maps, and mark reset status. Request descriptor flags and function codes determine whether outstanding Fusion commands represent SCSI I/O, LD I/O, passthrough MFI commands, or task management commands.

## State And Persistence Behavior

This header defines volatile in-memory and DMA state; it does not itself persist data. Firmware owns durable controller state. The driver stores firmware-derived snapshots in DMA buffers (`ld_map`, `pd_seq_sync`) and normalized non-DMA maps (`ld_drv_map`). `fusion_context` fields describe allocation sizes and queue depths so resources can be reused across normal I/O and rebuilt during OCR.

Endian annotations are part of the state contract. Firmware-facing numeric fields are commonly `__le16`, `__le32`, `__le64`, or `__be16`/`__be32` for SCSI EEDP CDB fields. Driver code must explicitly convert when reading or writing these fields.

The header also defines feature and policy bits that affect runtime state: fast-path capability, read-ahead capability, PI modes, cache bypass capability, region-lock request types, CPU affinity masks, write mode, LD state, stream detection, and RAID5/6 division-offload subtype.

## Dependencies

The header assumes Linux kernel type definitions, endian annotations, flexible-array helpers, static assertions, DMA address types, atomics, completions, SCSI command forward declarations, and MegaRAID common types from `megaraid_sas.h` included by users. It is tightly coupled to firmware ABI expectations, especially fixed offsets in `MPI2_RAID_SCSI_IO_REQUEST`, `RAID_CONTEXT`, `RAID_CONTEXT_G35`, request descriptors, reply descriptors, and RAID map layouts.

It also depends on constants defined elsewhere for adapter type, crash dump sizing, SCSI host state, target indexing, and common MFI command handling. The source files using this header supply those through their include of `megaraid_sas.h`.

## Risks And Edge Cases

The main risk is ABI drift. Any change to structure packing, field order, endian type, bitfield order, or fixed-size constants can break firmware communication. The big-endian bitfield branches in RAID capability, CPU affinity, and task-management flags must remain consistent with firmware layout. The static assertions around trailing overlap protect two map wrappers, but many other structures rely on implicit layout discipline.

Flexible and variable-size structures require careful allocation. `MR_FW_RAID_MAP`, `MR_FW_RAID_MAP_DYNAMIC`, `MR_PD_CFG_SEQ_NUM_SYNC`, `MR_DRV_RAID_MAP`, and `MPI2_RAID_SCSI_IO_REQUEST` all have flexible or overlayed trailing data. Callers must use the correct size for firmware generation, adapter capability, and queue depth; under-allocation can corrupt adjacent memory, while over-reading firmware-provided descriptor counts can copy beyond valid map data.

Bit packing is correctness-critical. `span_arm`, `r56_arm_map`, `routing_flags`, `raid_flags`, `nseg_type`, stream-detected bits, SGE counts, and descriptor `RequestFlags` are interpreted by firmware. A wrong shift or endian conversion can route I/O to the wrong path, disable locking, choose the wrong controller CPU, or misreport SGL length.

The driver-normalized map increases maximum dimensions to dynamic sizes (`MAX_LOGICAL_DRIVES_DYN`, `MAX_API_ARRAYS_DYN`, `MAX_RAIDMAP_PHYSICAL_DEVICES_DYN`). Code that still assumes legacy 64-LD or 256-PD limits can mismatch these structures. Conversely, firmware maps that report counts above the allocated limits must be rejected before copying.

## Test Signals

Compile-time signals include no structure-offset assertion failures, no flexible-array warnings, and clean builds on little-endian and big-endian configurations. Runtime signals include successful IOC init with correct request frame size, successful fast-path map validation across legacy, extended, and dynamic RAID maps, correct SGE counts for main and chained SGLs, correct NVMe PRP flags, task management replies decoded correctly, and reply descriptors returning valid SMIDs.

Regression tests should exercise adapters below and above `INVADER_SERIES`/`VENTURA_SERIES`, RDPQ and non-RDPQ reply modes, 64-bit and non-64-bit DMA capability negotiation, more-than-256 JBOD support, dynamic map descriptors, RAID1 peer SMID completion, stream-detection bit setting/clearing, and T10 PI CDB/EEDP fields.
