# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.c

## Purpose
`verbs.c` is the hfi1 verbs integration hub. It registers the device with rdmavt/IB core, advertises device and port capabilities, dispatches incoming packets by opcode and QP, builds TX descriptors for PIO or SDMA, handles pkey enforcement, manages send wait lists for memory/PIO pressure, and exposes hardware statistics and device operations.

## Important APIs and Functions
Exports include `hfi1_kdeth_eager_rcv()`, `hfi1_kdeth_expected_rcv()`, `hfi1_ib_rcv()`, `hfi1_16B_rcv()`, `hfi1_wait_kmem()`, `hfi1_verbs_send_dma()`, `hfi1_verbs_send_pio()`, `egress_pkey_check()`, `hfi1_verbs_send()`, `ah_to_sc()`, `hfi1_get_npkeys()`, `hfi1_register_ib_device()`, `hfi1_unregister_ib_device()`, and `hfi1_cnp_rcv()`. Important internal pieces are opcode tables, header-length tables, `qp_ok()`, `tid_qp_ok()`, `hfi1_handle_packet()`, `verbs_sdma_complete()`, `wait_kmem()`, `build_verbs_ulp_payload()`, `build_verbs_tx_desc()`, `update_hcrc()`, `pio_wait()`, `verbs_pio_complete()`, `get_send_routine()`, device/port query helpers, AH validation/update, stats allocation, and registration of rdmavt driver function callbacks.

## Control Flow
RX flow enters through 9B, 16B, or KDETH-specific receive functions. The code traces the header, increments opcode stats, looks up QPs under RCU, checks QP state/opcode compatibility, applies pkey checks for bypass packets, locks the QP receive side, and calls the registered opcode handler (`hfi1_rc_rcv`, `hfi1_uc_rcv`, `hfi1_ud_rcv`, TID RDMA handlers, or `hfi1_cnp_rcv`). Multicast delivery iterates attached QPs. TX flow enters `hfi1_verbs_send()`, extracts pkey/opcode from 9B or 16B headers, chooses PIO or DMA based on device capability, QP type, packet size, opcode, and pending iowait, enforces egress pkeys, and invokes the selected send routine. DMA builds SDMA descriptors and submits them; PIO allocates a PIO buffer and copies header/payload directly, queueing the QP if resources are unavailable. Registration initializes ports, timers, locks, txreq cache, IB device fields, rdmavt parameters/callbacks, ports, sysfs, and stats.

## State, Persistence, and Dependencies
Persistent state includes module parameters for resource limits and copy policy, global system image GUID, opcode/stat tables, `hfi1_ibdev` wait lists/timers/txreq cache, per-port SL/SC mappings, rdmavt device parameters, and cached stats descriptors. Runtime QP state is shared with rdmavt and hfi1 private QP fields. Dependencies include `hfi.h`, `device.h`, `qp.h`, `verbs_txreq.h`, `debugfs.h`, `fault.h`, `affinity.h`, `ipoib.h`, rdmavt, IB MAD/user verbs, and OPA address helpers.

## Integration Points
This file binds hfi1 to the RDMA core via `ib_device_ops` and `rvt_register_device()`. It connects transport-specific files (`rc.c`, `uc.c`, `ud.c`, TID RDMA code) to RX dispatch and send construction. It uses SDMA/PIO hardware helpers, pkey enforcement, congestion processing, MAD processing, IPoIB parameters, sysfs/debugfs, and QP lifecycle callbacks from `qp.c`.

## Risks and Test Signals
Risks include opcode table drift, pkey enforcement inconsistencies between 9B/16B/user/kernel paths, incorrect PIO-vs-SDMA choice under resource pressure, wait-list leaks, missed QP refcount wakeups, descriptor build rollback bugs, registration cleanup leaks, stats descriptor global lifetime issues with multiple devices, and CNP handling for unsupported QP types. Test signals include device register/unregister cycles, RC/UC/UD/TID traffic dispatch, multicast delivery, PIO buffer exhaustion and wakeup, SDMA descriptor build failures, pkey violation counters/completions, fault injection, hardware stats queries, AH validation, port shutdown, and CNP/BECN processing.
