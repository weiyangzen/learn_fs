# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.c

## Purpose

`qed_cxt.c` implements the QED driver's context manager for connection IDs, task IDs, ILT layout/allocation, searcher free-list memory, timer/search/parser/DQ/CDU/QM runtime initialization, and protocol-specific resource sizing. It is central to PF bring-up because the firmware and hardware blocks need a consistent view of where CDUC connection contexts, CDUT task contexts, QM/TM/SRC/TSDM memory, and VF regions live in ILT space.

## Important APIs, Types, and Functions

- Context sizing unions: `conn_context`, `type0_task_context`, and `type1_task_context` define the maximum-sized per-protocol context payloads used by `CONN_CXT_SIZE()`, `TYPE0_TASK_CXT_SIZE()`, and `TYPE1_TASK_CXT_SIZE()`.
- Resource counters: `qed_cxt_cdu_iids()`, `qed_cxt_src_iids()`, `qed_cxt_tm_iids()`, and `qed_cxt_qm_iids()` aggregate PF/VF CID and TID counts from `p_hwfn->p_cxt_mngr->conn_cfg`.
- ILT layout: `qed_cxt_cfg_ilt_compute()` is the major layout pass. It resets block descriptors, computes client first/last lines, block sizes, PF/VF spans, dynamic RoCE CDUC skip lines, SRC/TM/TSDM sizing, and rejects configurations exceeding `RESC_NUM(p_hwfn, QED_ILT)`.
- Allocation/free: `qed_cxt_mngr_alloc()`, `qed_cxt_tables_alloc()`, and `qed_cxt_mngr_free()` allocate the manager, ILT shadow DMA pages, SRC T2 pages, and CID bitmaps, and unwind them on failure.
- Hardware initialization: `qed_cxt_hw_init_common()` programs CDU common and parser common settings; `qed_cxt_hw_init_pf()` sequences QM, CM, DQ, CDU PF, ILT, SRC, TM, and parser PF runtime-register initialization.
- CID lifecycle: `_qed_cxt_acquire_cid()`, `qed_cxt_acquire_cid()`, `_qed_cxt_release_cid()`, `qed_cxt_release_cid()`, `qed_cxt_get_cid_info()`, and `qed_cxt_test_cid_acquired()` manage per-protocol PF/VF CID bitmaps and return context pointers.
- Protocol sizing: `qed_cxt_set_pf_params()` maps the active PCI personality to CORE, ETH, RDMA, FCoE, iSCSI, or NVMe/TCP CID/TID requirements. `qed_rdma_set_pf_params()` has special RoCE/iWARP behavior and SRQ/XRC-SRQ sizing.
- Dynamic ILT: `qed_cxt_dynamic_ilt_alloc()` lazily allocates RoCE-oriented CDUC, CDUT, TSDM SRQ, and XRC SRQ pages and writes the wide-bus PSWRQ2 ILT entry via DMAE. `qed_cxt_free_proto_ilt()` frees protocol-related dynamic ranges.
- Task helpers: `qed_cxt_get_tid_mem_info()` and `qed_cxt_get_task_ctx()` expose task working/forced-load memory for storage personalities. Page count helpers report CDUT work/init pages for PF/VF.

## Control Flow

Initialization is staged. First `qed_cxt_mngr_alloc()` creates the manager, initializes ILT client register offsets and default 64K ILT page sizes, computes context/task sizes, captures SR-IOV VF counts, initializes the dynamic allocation mutex, and attaches the manager to `p_hwfn`. Then `qed_cxt_set_pf_params()` fills protocol resource counts from personality-specific PF parameters. `qed_cxt_cfg_ilt_compute()` converts those counts into client block layout and total ILT line usage. `qed_cxt_tables_alloc()` allocates memory backing for non-dynamic ILT lines, SRC T2 pages, and CID acquisition maps.

During PF hardware initialization, `qed_cxt_hw_init_common()` stores CDU common sizing and parser-common settings into runtime arrays. `qed_cxt_hw_init_pf()` calls the per-block initialization functions in dependency order: QM gets resource totals, DQ gets cumulative protocol CID ranges, CDU gets CDUT segment offsets, ILT gets bounds and physical entries, SRC gets T2 free-list registers, TM gets PF/VF timer-memory descriptors, and parser gets FCoE task limits when applicable.

Runtime CID acquisition scans the correct PF or VF bitmap for the first clear bit, marks it, and returns `start_cid + rel_cid`. Release verifies the CID belongs to an acquired protocol range before clearing the bit. CID info lookup repeats the verification, computes the CDUC ILT line and offset, and fails if the line is not allocated, which matters for dynamic RoCE allocation.

Dynamic ILT allocation is serialized by `p_cxt_mngr->mutex`. It selects the ILT client/block and element size from `enum qed_cxt_elem_type`, computes the ILT line from `iid`, allocates one DMA page if absent, patches RoCE task TDIF ref-tag masks for task pages, records the shadow descriptor, writes the hardware ILT entry through DMAE, and updates parser RDMA search state for connection contexts.

## State and Persistence Behavior

All durable-in-driver state is attached to `struct qed_cxt_mngr` under `p_hwfn->p_cxt_mngr`. It persists for the hardware function lifetime and includes protocol resource configuration, ILT client layout, task type sizes, VF counts, CID acquisition bitmaps, the ILT shadow descriptor array, the SRC T2 DMA free-list metadata, SRQ/XRC counts, ARFS counts, and cached page counters/context sizes. Hardware-visible state is written through runtime-register storage macros, direct GRC writes, or DMAE writes; it must be recreated on device initialization and is freed on manager teardown. CID bitmap contents are reset by `qed_cxt_mngr_setup()` but not persisted across reload.

## Dependencies and Integration Points

The file depends on QED hardware and firmware interface headers (`qed_hsi.h`, `qed_reg_addr.h`, `qed_init_ops.h`), core device state (`qed.h`, `qed_dev_api.h`, `qed_hw.h`), SR-IOV metadata (`qed_sriov.h`), RDMA parameters (`qed_rdma.h`), Linux DMA allocation, bitmaps, mutexes, and logging. It integrates with QM initialization/reconfiguration (`qed_qm_pf_rt_init`, `qed_qm_pf_mem_size`, `qed_get_cm_pq_idx`), parser RDMA/FCoE settings, DMAE, PTT acquisition, and slowpath updates that need CID/task context pointers.

## Risks and Edge Cases

- ILT arithmetic is sensitive to resource counts, alignment, and per-page element sizes. A bad count can overrun `RESC_NUM(QED_ILT)` or misprogram first/last lines.
- Several paths assume only one protocol owns a TID segment. `qed_cxt_tid_seg_info()` returns the first segment with a nonzero count.
- Dynamic RoCE allocation intentionally leaves some ILT shadow lines absent at initial allocation. Callers of `qed_cxt_get_cid_info()` must tolerate `-EINVAL` until pages are allocated.
- `qed_cxt_free_ilt_range()` iterates `i < shadow_end_line`; boundary correctness is important for freeing the last page in a range.
- DQ register programming is manually cumulative for protocol indexes 0 through 5 and then mirrors values to 6 and 7, so protocol enum changes would need careful updates.
- SRC T2 setup assumes entries per page is a power of two and builds a DMA-address linked list consumed by hardware.
- Dynamic allocation holds a mutex while acquiring PTT and allocating DMA memory, so failure handling and release paths must remain balanced.

## Test Signals

Useful signals are kernel build coverage for QED with Ethernet, RDMA, FCoE, iSCSI, NVMe/TCP, SR-IOV, and DCB combinations; boot/probe logs with `QED_MSG_ILT` and `QED_MSG_CXT`; resource-limit tests that intentionally exceed ILT lines and verify `-EINVAL`; CID acquire/release exhaustion tests; RDMA workloads that trigger dynamic ILT allocation and teardown; storage offload tests that use task memory helpers; and device reload/SR-IOV enable-disable cycles that exercise allocation unwind and bitmap reset.
