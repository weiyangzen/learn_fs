# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_roce_hsi.h lines 5907-6450

## Scope

This chunk covers the tail of the generated Broadcom `bng_re` RoCE hardware/software interface header. It starts inside the v2 raw Ethernet/QP1 receive CQE definition and then defines the v3 completion queue entry formats, notification queue entry formats, XRRQ records, and PTU page-table records used by the driver and firmware ABI. The file is generated and intentionally contains packed hardware layout structs plus masks/shifts; it has no executable functions.

The covered records are:

- Tail fields of `struct cq_res_raweth_qp1_v2`.
- `struct cq_terminal` and `struct cq_cutoff`.
- v3 CQEs: `cq_req_v3`, `cq_res_rc_v3`, `cq_res_ud_v3`, `cq_res_raweth_qp1_v3`, and `cq_res_ud_cfa_v3`.
- NQEs: `nq_base`, `nq_cn`, `nq_srq_event`, `nq_dbq_event`, and `nq_reassign`.
- XRRQ queue records: `xrrq_irrq` and `xrrq_orrq`.
- PTU translation records: `ptu_pte` and `ptu_pde`.

## Purpose

This section is the ABI map for DMA-visible queue entries exchanged between the `bng_re` RDMA driver and RoCE firmware/hardware. The CQE structures describe how completions are reported back to software, including send completions, reliable-connected receive completions, unreliable datagram completions, raw Ethernet/QP1 receive completions, CFA-enriched receive completions, terminal entries, and CQ cut-off entries. The NQE structures describe interrupt/notification records that point software toward CQs, SRQs, doorbell queues, or reassigned notification queues. The XRRQ records describe inbound and outbound read/atomic request queue entries. The PTU records describe page table entries and directory entries used by the driver's page buffer list (PBL) allocator.

The parent `cq_base` layout earlier in the same header defines the shared 32-byte CQE discriminator byte. These v3 CQEs use `cqe_type_toggle` bits compatible with `CQ_BASE_CQE_TYPE_REQ_V3`, `RES_RC_V3`, `RES_UD_V3`, `RES_RAWETH_QP1_V3`, and `RES_UD_CFA_V3`, while the NQE records use `nq_base.info10_type` type values such as CQ notification, SRQ event, DBQ event, QP event, function event, and NQ reassignment.

## Important Types and Fields

`cq_res_raweth_qp1_v2` tail fields carry raw Ethernet/QP1 receive classification metadata. The covered lines include checksum status fields, completion checksum, CFA metadata, the CQE type/toggle byte, status values, SRQ-vs-RQ selection, receive WR ID, TPID selection metadata, VLAN validity, and raw payload offset.

`cq_terminal` is a 32-byte terminal CQE. It carries `qp_handle`, send and receive consumer indices, a `CQ_TERMINAL_CQE_TYPE_TERMINAL` discriminator, and an OK-only status. It marks an end or terminal condition in a CQ stream rather than a normal work completion.

`cq_cutoff` is another special 32-byte CQE. It carries `CQ_CUTOFF_CQE_TYPE_CUT_OFF`, OK-only status, and `CQ_CUTOFF_RESIZE_TOGGLE_MASK`, which is likely consumed during CQ resize/cutoff handling to distinguish old and new CQ buffers.

`cq_req_v3` is the v3 request/send-side completion. It reports `qp_handle`, `sq_cons_idx`, `opaque`, the v3 request CQE type, a `PUSH` flag, and a broad IB-style status set: bad response, local length/QP/protection/memory-management errors, remote request/access/operation errors, RNR retry exhaustion, transport retry exhaustion, flushed work request, and overflow.

`cq_res_rc_v3` is the v3 reliable-connected receive completion. It reports payload `length`, immediate data or invalidated R_Key, `qp_handle`, `mr_handle`, status, and flags identifying SRQ origin, immediate data, invalidate, and whether the receive represents SEND or RDMA WRITE data.

`cq_res_ud_v3` is the v3 unreliable datagram receive completion. It reports a 14-bit `length`, source QP split across `src_qp_high` and `src_qp_low`, immediate data, `qp_handle`, source MAC, status, SRQ/IMM flags, and RoCE IP version (`V1`, `V2IPV4`, `V2IPV6`).

`cq_res_raweth_qp1_v3` is the richest v3 receive CQE in this chunk. It reports length, packet classification (`ITYPE_*` including IP, TCP, UDP, FCoE, RoCE, ICMP, and PTP), packet error summaries, tunnel packet errors, VLAN/CFA metadata, QP handle, checksum calculation flags, metadata format, IP version hints, complete checksum, CQE type, receive status, SRQ flag, payload offset, and opaque software data. Compared with v2, v3 adds explicit `VNIC_ID` metadata format, tunnel IP type, and an extra L4 SUPAR CRC packet error.

`cq_res_ud_cfa_v3` is a v3 UD receive completion with CFA metadata. It combines payload length, VLAN priority/VID/DE metadata, immediate data, queue ID, TPID metadata, source QP, metadata2, source MAC, status, SRQ/IMM flags, RoCE IP version, and metadata format values including action-record pointer, tunnel ID, CHDR data, header offset, and VNIC ID.

`nq_base` is the generic 16-byte notification queue entry used for dispatch. Its `info10_type` low bits select the event class and its high bits provide auxiliary info. `info63_v[2]` carries a valid bit and a 63-bit information payload.

`nq_cn`, `nq_srq_event`, `nq_dbq_event`, and `nq_reassign` specialize `nq_base`. CQ notifications carry a CQ handle split into low/high words plus a two-bit toggle. SRQ events carry a threshold event and SRQ handle. DBQ events carry DB PFID, DPI, DB XID, and DB type. NQ reassignment carries a CQ handle and valid bit.

`xrrq_irrq` and `xrrq_orrq` are 32-byte read/atomic request records. Both encode request type as read or atomic and carry 24-bit PSNs. IRRQ additionally carries credits, MSN, virtual address or atomic result, R_Key, and length. ORRQ carries number of SGEs, length, end PSN, first SGE physical address or single-SGE VA, single SGE L_Key, and single SGE size.

`ptu_pte` and `ptu_pde` are 8-byte PTU page translation records. Both use a 4 KiB-aligned page address mask. PTEs add `VALID`, `LAST`, and `NEXT_TO_LAST` bits; PDEs add `VALID`. These constants are actively used by `bng_res.c` when building the DMA page-buffer-list hierarchy for hardware queues.

## Control Flow and Data Flow

This header chunk itself has no runtime control flow. Runtime dispatch is driven by queue consumers that read a base entry, validate its toggle/valid state, apply a memory barrier, then decode the type field and cast to the specialized structure. That pattern is implied by the shared `cq_base` and `nq_base` discriminators in this file and is visible in the sibling Broadcom `bnxt_re` code paths for similar HSI definitions. In `bng_re`, the lower-level queue helpers in `bng_res.h` provide `bng_re_get_qe()` for indexed access into HWQ pages and doorbell helpers for CQ/NQ progress.

The PTU portion has direct local control flow in `bng_re_alloc_init_hwq()` in `bng_res.c`. The allocator rounds queue depth and stride to powers of two, computes required pages, allocates coherent DMA pages, and chooses a 0-, 1-, or 2-level PBL topology. For multi-page queues, it writes DMA addresses into PBL/PDE pages with `PTU_PTE_VALID`. For queue-type HWQs it additionally marks the last and next-to-last entries with `PTU_PTE_LAST` and `PTU_PTE_NEXT_TO_LAST`. It then records producer/consumer indices, queue element size, entries-per-page, and direct PBL pointers used by queue accessors.

## State and Persistence Behavior

All structures in this chunk represent transient, DMA-visible hardware state, not durable filesystem or userspace persistence. CQEs and NQEs live in coherent queue memory allocated elsewhere and are consumed by software through producer/consumer indices, valid bits, and toggle/epoch bits. The driver must treat multi-byte fields as little-endian (`__le16`, `__le32`, `__le64`) and convert them before interpretation.

The persistent-in-memory state most directly tied to this chunk is the HWQ/PBL state in `struct bng_re_hwq`: PBL level, page arrays, DMA address arrays, `prod`, `cons`, `max_elements`, `element_size`, and `qe_ppg`. `bng_re_free_hwq()` releases the coherent pages and resets those state fields. The PTU entry contents persist only as long as their owning HWQ is allocated and registered with firmware/hardware.

## Dependencies and Integration Points

The header depends on kernel fixed-width little-endian types and includes `<linux/bnge/hsi.h>` for shared Broadcom doorbell and command ABI definitions. Consumers must also use the resource helpers in `bng_res.h` and `bng_res.c` for queue memory layout, doorbell state, and PBL construction.

Key integration points are:

- Completion queue creation and polling: CQ buffers use 32-byte entries matching `sizeof(struct cq_base)` and the specialized CQE layouts here.
- Notification queue servicing: NQ buffers use 16-byte entries matching `sizeof(struct nq_base)`, with CQ notification, SRQ threshold, DBQ threshold, and reassignment event formats.
- Queue doorbells: CQ/NQ consumer advancement must remain synchronized with the valid/toggle fields encoded in these entries.
- Raw Ethernet/QP1 and UD/CFA receive paths: packet classification, checksum, VLAN/CFA metadata, source addressing, and RoCE IP version are surfaced only through these CQE fields.
- HWQ allocation: `ptu_pte`/`ptu_pde` flags are used to build PBL address chains passed to firmware for command queues, completion/event queues, and future fast-path queues.

## Risks and Edge Cases

The largest risk is ABI drift. This file is generated and the bit layouts must match firmware exactly; changing struct sizes, field order, masks, or discriminator values would corrupt DMA interpretation. Compile-time checks for `sizeof(struct cq_base) == 32`, `sizeof(struct nq_base) == 16`, and PTU record size would catch some accidental drift.

CQ/NQ consumers must validate the entry before reading the rest of the record and must use DMA read barriers so hardware writes are visible in order. Skipping that ordering can expose stale handles, stale status, or partially written metadata.

The status values differ across CQE generations and types. Code that maps hardware statuses to IB work completion statuses must use the matching CQE type's status domain; treating v3 raw/UD statuses like older v1/v2 values can misclassify local access, hardware length, flush, or overflow errors.

Raw Ethernet and UD/CFA metadata fields are densely packed and versioned. `VNIC_ID` is valid in v3 metadata-format fields but not all older variants. Packet error encodings also differ between v2 and v3. Consumers should mask and shift rather than compare unmasked raw words.

PBL construction currently writes DMA addresses ORed with PTU flags into `dma_addr_t`-typed memory. This relies on coherent allocation, correct 4 KiB alignment, and little-endian expectations. The local code does not visibly wrap these stores in `cpu_to_le64()`, so cross-endian support would need audit if this driver is ever used outside little-endian platforms.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage with warnings enabled to catch generated-struct type or size regressions.
- Static assertions or debug checks for 32-byte CQEs, 16-byte NQEs, and 8-byte PTU records.
- HWQ allocation tests across page-count boundaries: one page, exactly 512 pages, more than 512 pages, `nopte` true, queue type, and context type.
- Runtime CQ/NQ tests that exercise v3 send, RC receive, UD receive, raw QP1 receive, UD/CFA receive, terminal, cut-off, CQ notification, SRQ threshold, DBQ threshold, and NQ reassignment entries.
- Error-injection or firmware test cases for each CQE status family, especially flushed, hardware flush, overflow, local protection, remote access, retry exhaustion, and raw packet checksum/error paths.
- Packet tests for VLAN/CFA metadata, metadata format variants, RoCE v1/v2 IPv4/v2 IPv6, tunnel checksum flags, complete checksum, and raw payload offset.
