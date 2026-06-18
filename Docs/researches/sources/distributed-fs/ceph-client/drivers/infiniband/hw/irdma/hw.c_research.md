# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/hw.c

## Purpose
`hw.c` is the main IRDMA control/runtime hardware orchestration file. It creates and destroys CQP, CCQ, CEQs, AEQ, HMC objects, PBLE resources, VSI runtime state, iWARP PUDA queues, resource bitmaps, local MAC/ARP/APBVT entries, qhash entries, and QP flush/AE control operations.

## Important APIs, types, and functions
Public entry points include `irdma_ctrl_init_hw`, `irdma_ctrl_deinit_hw`, `irdma_rt_init_hw`, `irdma_rt_deinit_hw`, `irdma_initialize_hw_rsrc`, `irdma_cqp_ce_handler`, `cqp_compl_worker`, `irdma_next_iw_state`, `irdma_manage_arp_cache`, `irdma_manage_qhash`, `irdma_hw_flush_wqes`, `irdma_gen_ae`, and `irdma_flush_wqes`. Important internal paths include AEQ/CEQ processing, CQP/CCQ/CEQ/AEQ creation and destruction, HMC setup, PBLE initialization, and APBVT/local MAC management.

## Control flow, state, and persistence
Control initialization proceeds through `irdma_ctrl_init_hw`: setup init memory, create CQP, query features, configure HMC/FPM and HMC objects, initialize resource bitmaps, create CCQ, create CEQ0 and extra CEQs, initialize PBLE chunks, and create/configure AEQ. Each completed phase updates `rf->init_state`, allowing `irdma_ctrl_deinit_hw` to fall through in reverse order after failures or unload. Runtime initialization initializes VSI state, CM core, stats, iWARP ILQ/IEQ if needed, MAC/IP state, cleanup workqueue, and used-resource counters. Interrupt flow moves from IRQ handler to tasklet to CEQ/AEQ polling, CQP completion worker, QP event dispatch, and user callbacks. State persists in `struct irdma_pci_f`, `struct irdma_device`, HMC/PBLE tables, resource bitmaps, CM hashes, and workqueues until teardown.

## Dependencies and integration points
`hw.c` depends on generation-specific data installed in `rf->gen_ops`, `dev->irq_ops`, register maps, HMC functions, PBLE functions, CQP/CCQ/CEQ/AEQ low-level routines, RDMA core ibdev event callbacks, netdev state, workqueues, tasklets, spinlocks, and auxiliary driver setup. Gen1, Gen2, and Gen3 interface files all converge on `irdma_ctrl_init_hw` and Gen1/Gen2/vport paths call `irdma_rt_init_hw`.

## Risks and test signals
Highest-risk areas are partial initialization cleanup, asynchronous AEQ/CEQ races with CQ/QP deletion, CQP request lifetime and deferred completion, flush retry edge cases, shared versus dedicated MSI-X vector indexing, and reset paths that bypass hardware commands. Test signals include staged failure injection at every `init_state`, interrupt storm and stale CEQE scenarios, qhash/APBVT add-delete races, QP flush with new SQ work posted during flush, RoCE versus iWARP mode coverage, and Gen1/Gen2/Gen3 hardware capability differences.
