# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/bnx2i.h

## Purpose

`bnx2i.h` is the shared private header for the NetXtreme II iSCSI offload driver. It defines driver limits, queue sizes, device-family flags, doorbell constants, statistics helpers, adapter/connection/endpoint/queue structures, global variables, and cross-file prototypes.

## Important APIs, Types, and Functions

Major structures include `struct generic_pdu_resc`, `struct bd_resc_page`, `struct io_bdt`, `struct bnx2i_cmd`, `struct bnx2i_conn`, `struct iscsi_cid_queue`, `struct bnx2i_stats_info`, `struct bnx2i_hba`, queue entry wrappers `struct sqe/rqe/cqe`, 577xx doorbell structures, `struct qp_info`, `struct ep_handles`, `struct bnx2i_endpoint`, `struct bnx2i_work`, and `struct bnx2i_percpu_s`.

Important enums and flags include adapter states, endpoint states, device-family bits for 5706/5708/5709/57710, mailbox access modes, and queue doorbell offsets. Prototypes expose CNIC callbacks, HBA allocation, connection lookup, QP allocation, WQE send routines, completion processing, endpoint lookup, doorbell mapping, and per-CPU I/O thread entry.

## Control Flow

The header defines the driver layering. `bnx2i_init.c` owns module and CNIC lifecycle, `bnx2i_hwi.c` owns hardware WQE/CQE handling, `bnx2i_iscsi.c` owns libiscsi transport/session/endpoint operations, and `bnx2i_sysfs.c` exports attributes. Runtime code threads through `struct bnx2i_hba` to `struct bnx2i_endpoint`, `struct bnx2i_conn`, and `struct bnx2i_cmd`.

## State and Persistence Behavior

All state is runtime-only. Persistent-looking data includes adapter lists, CNIC registration state, per-HBA CID queues, endpoint lists, QP DMA memory, generic PDU DMA buffers, command BD tables, statistics, adapter state bits, endpoint state bits, per-CPU work queues, and firmware context IDs. The header also declares module parameters such as queue sizes, event coalescing, delayed ACK, and error masks.

## Dependencies and Integration Points

It includes Linux PCI, networking, kthread, CPU hotplug, SCSI, libiscsi, iSCSI transport, CNIC, HSI, and bnx2x management firmware request headers. It is the common contract across all bnx2i source files and the CNIC callback table.

## Risks and Edge Cases

Structure layout and constants directly drive firmware-visible DMA and MMIO behavior. Queue size limits vary by device family, and 577xx doorbells/page tables differ from 570x devices. State bits are shared across process context, softirq/KCQ callbacks, kthreads, timers, and network events, so locking expectations must be respected by all users. Statistics helpers differ for 32-bit and 64-bit builds.

## Test Signals

Useful signals include all architecture builds, structure size/alignment checks for firmware layouts, queue-size module parameter tests, adapter state transitions under netdev up/down, endpoint state transitions through connect/disconnect, per-CPU completion processing, stats retrieval, and sparse/lockdep coverage.
