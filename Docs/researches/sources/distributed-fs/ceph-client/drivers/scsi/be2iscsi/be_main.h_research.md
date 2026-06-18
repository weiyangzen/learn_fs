# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_main.h

## Purpose

`be_main.h` is the central private header for the `be2iscsi` Linux kernel driver. It defines driver identity, supported PCI IDs, resource limits, hardware register offsets, doorbell bit fields, memory descriptor indices, main HBA/session/connection/task structures, firmware-facing WRB/SGL/CQE/PDU layouts, async default-PDU bookkeeping, and prototypes shared with peer implementation files. It is the type contract that lets `be_main.c`, `be_mgmt.c`, `be_iscsi.c`, and command helpers share the same view of HBA state and hardware descriptors.

## Important APIs, Types, And Constants

Driver identity constants include `DRV_NAME`, `BUILD_STR`, `BE_NAME`, `DRV_DESC`, vendor IDs, and device IDs for BE2, BE3, OneConnect, and Skyhawk-R adapters. Capacity constants define queue and protocol limits such as `BE2_IO_DEPTH`, `BE2_MAX_SESSIONS`, `BE2_SGE`, default PDU sizes, max CPUs, SCSI host limits, sense-buffer sizing, minimum memory fragment size, and maximum command size.

Hardware-facing macros define PCI config offsets, host interrupt mask, CEV ISR register offsets, TX/RX doorbell offsets, EQ/CQ doorbell masks and shifts, default-PDU queue access, page-count calculations, and ULP/CID helpers. State macros define online/error bits and `beiscsi_hba_is_online`.

Important structures include:

- `struct beiscsi_hba`: the main adapter state, including resource parameters, hardware controller pointer, DMA memory descriptors, mapped BAR addresses, PCI device, IRQ/MSI-X names, SGL handle pools, endpoint/connection tables, firmware configuration, state bits, timers/work items, control/MCC state, generation, interface handle, AIC state, selected I/O writer, and boot-session state.
- `struct hwi_controller`, `struct hwi_context_memory`, `struct hwi_wrb_context`, and `struct wrb_handle`: WRB queue and context structures mapping firmware CIDs/CRIs to WRB rings and handles.
- `struct sgl_handle`, `struct iscsi_sge`, `struct mem_array`, and `struct be_mem_descriptor`: DMA memory and SGL bookkeeping used for I/O, management, and firmware-posted SGL pages.
- `struct beiscsi_conn`, `struct beiscsi_session`, and `struct beiscsi_io_task`: libiscsi private state for sessions, connections, and tasks.
- `struct hd_async_context`, `struct hd_async_entry`, `struct hd_async_buf_context`, and `struct hd_async_handle`: default-PDU header/data buffer state used to gather unsolicited or firmware-unprocessed iSCSI PDUs.
- Hardware-layout structures and pseudo-AMAP structures for PDU headers, SCSI/data-out BHS, NOP, SGL entries, offload params, solicited CQEs, default-PDU CQEs, EQ entries, CQ doorbells, WRBs, and target-context-update WRBs.

The header declares shared functions such as `alloc_wrb_handle`, `free_mgmt_sgl_handle`, `beiscsi_free_mgmt_task_handles`, `hwi_ring_cq_db`, `beiscsi_process_cq`, `beiscsi_process_mcc_cq`, and `beiscsi_start_boot_work`.

## Control Flow Role

This header does not execute control flow directly, but it shapes the driver lifecycle. Probe fills `struct beiscsi_hba`, creates `struct hwi_controller`, populates `struct hwi_context_memory`, builds memory descriptors indexed by `enum be_mem_enum`, and initializes WRB/SGL/default-PDU contexts described here. I/O submission allocates `struct beiscsi_io_task`, `struct wrb_handle`, and `struct sgl_handle`, fills `struct iscsi_wrb` using AMAP pseudo-layouts, and links completions back through `wrb_handle->pio_handle`. CQ processing decodes `struct sol_cqe` and default-PDU CQEs using the masks and pseudo-AMAP definitions. Recovery and cleanup use state bits and pointer ownership encoded in `struct beiscsi_hba`.

## State And Persistence Behavior

All structures in this header represent volatile kernel driver state or firmware DMA descriptors. `struct beiscsi_hba` is the root object attached to the SCSI host and PCI device. Its `fw_config` substructure is a cached view of firmware-provided resource assignments, including ULP support, CID/ICD ranges, chain ranges, physical port, features, and queue counts. Its `boot_struct` caches firmware boot session data until boot sysfs objects are created. Persistent configuration is not stored by the header itself; fields such as initiator name, IP configuration, gateway, VLAN, flash contents, and boot target are accessed through firmware commands defined elsewhere.

Pool state is tracked with circular indices and availability counters for IO SGLs, management SGLs, ULP CID arrays, and WRB handles. Error state is represented as bit positions in `phba->state`, with `BEISCSI_HBA_IN_ERR` grouping PCI, firmware timeout, UE, and TPE errors. Async PDU state includes per-CRI wait queues for in-progress header/data gather operations and CID-to-async-CRI mapping.

## Dependencies And Integration Points

The header includes Linux kernel, PCI, Ethernet/IP, module, SCSI, libiscsi, and scsi_transport_iscsi headers, then includes local `be.h` after defining ULP and HBA-related types. It depends on firmware command definitions from `be_cmds.h` indirectly through embedded command headers and response structures used by peer files. The AMAP pseudo-structures integrate with local AMAP bit helpers used throughout the driver.

External integration is with PCI device IDs, SCSI host configuration, libiscsi task/session/connection objects, hardware BAR doorbells, DMA memory, firmware queue descriptors, and iSCSI boot sysfs. The data layouts must match firmware ABI expectations; even small field-width or endianness changes can break hardware communication.

## Risks And Edge Cases

The biggest risk is ABI drift. Many pseudo-AMAP structures encode bit positions by field width rather than ordinary C layout semantics, so changes must be synchronized with the `AMAP_SET_BITS`/`AMAP_GET_BITS` users and firmware documentation. Several comments warn that variable-size arrays must remain last, that command-per-LUN must align with invalidation table size, and that async PDU buffers have hardware-required posting multiples.

`BE_MAX_SESSION` limits CID map arrays to 2048; any firmware generation exposing larger CID values would require coordinated changes. ULP support is represented as bits and indexed arrays of size two, so multi-ULP assumptions are hardcoded. `struct beiscsi_hba` is broad and shared across many contexts; modifications can introduce locking, lifetime, or initialization-order regressions.

## Test Signals

Header changes should be validated by full kernel compilation with `CONFIG_SCSI_BE2ISCSI`, sparse/endian warnings, structure size and field-offset review for firmware-facing descriptors, and runtime smoke tests covering BE2/BE3 and Skyhawk paths if hardware is available. Test focus should include CID/CRI mapping, WRB allocation, SGL page posting, async PDU gather, error-state gating, and boot sysfs object creation.
