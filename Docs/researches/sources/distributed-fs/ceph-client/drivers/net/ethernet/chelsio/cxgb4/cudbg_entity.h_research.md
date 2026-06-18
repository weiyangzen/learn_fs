# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_entity.h

## Purpose
This header defines the on-wire/in-buffer entity payload structures used by cxgb4 CUDBG dumps. It describes mailbox logs, CIM/TP/SGE/PM/PCIE snapshots, memory maps, TID/TCAM data, VPD, logic-analyzer captures, PBT tables, queue descriptors, and constants needed to decode them.

## Important APIs, Types, And Functions
The key types are `struct cudbg_mbox_log`, `cudbg_cim_qcfg`, `cudbg_pm_stats`, `cudbg_hw_sched`, `ireg_field`/`ireg_buf`, `cudbg_meminfo`, `cudbg_tid_info_region_rev1`, `cudbg_mps_tcam`, `cudbg_tcam`, `cudbg_tid_data`, `cudbg_ulptx_la`, `cudbg_pbt_tables`, and `cudbg_qdesc_*`. `enum cudbg_le_entry_types` classifies LE/TID entries. Revision macros such as `CUDBG_MEMINFO_REV`, `CUDBG_TID_INFO_REV`, `CUDBG_ULPTX_LA_REV`, and `CUDBG_QDESC_REV` version selected payloads.

## Control Flow
The header has no executable flow, but it defines layouts that collector functions fill. Several structures have flexible arrays (`cudbg_tp_la`, `cudbg_cim_pif_la`, `cudbg_qdesc_entry`, `cudbg_qdesc_info`) so collectors must compute exact sizes and keep these fields last.

## State And Persistence
These structures are serialized into a CUDBG dump buffer, which may be returned through ethtool or vmcore device dump. The state is a snapshot of live adapter hardware/software state at collection time, not a mutable runtime owner.

## Dependencies And Integration Points
The header depends on many constants from cxgb4/t4 register and firmware headers via includers. It is included by `cxgb4_cudbg.h`, `cudbg_lib.c`, and decoding consumers. `cudbg_region[]` is a static string table used by memory-region mapping code in `cudbg_lib.c`.

## Risks
Layout changes can break dump decoder compatibility. Flexible-array size miscalculations can corrupt subsequent entities. The `cudbg_region[]` ordering is semantically tied to memory-region indexes used by `cudbg_fill_meminfo()` and context dump logic. Endianness is mixed: collectors must explicitly encode or decode hardware data where required.

## Test Signals
Build-time structure-size checks, dump decode compatibility tests, LE/TCAM and qdesc parser tests, and sample dumps across T4/T5/T6 hardware are important. Versioned entities should be validated by old and new decoder tools.
