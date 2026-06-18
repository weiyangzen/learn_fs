# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_hw4.h

## Purpose

`lpfc_hw4.h` is the SLI-4 hardware contract header for the Broadcom/Emulex LPFC Fibre Channel driver. It defines register offsets, queue entry layouts, mailbox command payloads, scatter/gather descriptors, completion formats, async event payloads, and WQE formats used by the driver to talk to SLI-4 adapters. The file has no executable functions beyond access macros, but it is a central ABI boundary between host driver code and adapter firmware/hardware.

The header is included broadly by LPFC implementation files such as `lpfc_init.c`, `lpfc_sli.c`, `lpfc_mbox.c`, `lpfc_scsi.c`, `lpfc_nvme.c`, `lpfc_nvmet.c`, `lpfc_els.c`, `lpfc_hbadisc.c`, `lpfc_bsg.c`, `lpfc_attr.c`, `lpfc_debugfs.c`, `lpfc_mem.c`, `lpfc_nportdisc.c`, `lpfc_vmid.c`, and `lpfc_vport.c`. It also depends on Fibre Channel UAPI definitions from `<uapi/scsi/fc/fc_fs.h>` and `<uapi/scsi/fc/fc_els.h>`, and on other kernel types available from the including compilation units (`u32`, `__le32`, `__be32`, `dma_addr_t`, `list_head`, `fcp_cmnd`, `fcp_rsp`).

## Important APIs, Types, and Constants

The header's lowest-level API is the bitfield helper family:

- `bf_get`, `bf_set` operate on native-endian 32-bit fields using the `name_SHIFT`, `name_MASK`, and `name_WORD` triplets declared beside each hardware field.
- `bf_get_le32`, `bf_set_le32`, and `bf_get_be32` add endian conversion for fields stored in little- or big-endian words.
- `get_wqe_reqtag`, `get_wqe_tmo`, `get_job_ulpword`, `set_job_ulpstatus`, and `set_job_ulpword4` are convenience macros for common WQE/completion access.

Core register and adapter-identification structures include `struct dma_address`, `struct lpfc_sli_intf`, `struct lpfc_asic_id`, and `struct lpfc_register`. These describe SLI interface discovery, ASIC family/revision decoding, physical/virtual function type, and generic BAR register access. Constants define supported SLI interface families from older BE/Lancer generations through G6, G7, G7P, and G8.

Queue-related hardware formats are a major part of the file:

- Event, completion, receive, and release entries: `struct lpfc_eqe`, `struct lpfc_cqe`, `struct lpfc_wcqe_complete`, `struct lpfc_wcqe_release`, `struct sli4_wcqe_xri_aborted`, `struct lpfc_rcqe`, and `struct lpfc_rqe`.
- Queue contexts and mailbox create/destroy payloads: `struct eq_context`, `struct cq_context`, `struct wq_context`, `struct rq_context`, `struct mq_context`, and the `lpfc_mbx_*_{eq,cq,wq,rq,mq}_create/destroy` command structures.
- Doorbell register offsets and fields for RQ, WQ, EQ/CQ, MQ, bootstrap mailbox, and if_type 6 variants.

Mailbox support is defined around `struct lpfc_sli4_cfg_mhdr`, `union lpfc_sli4_cfg_shdr`, `struct mbox_header`, and `struct lpfc_mqe`. `struct lpfc_mqe` is the mailbox queue entry union that overlays a 64-word mailbox with all supported command payloads: SLI4 config, queue creation, resource extent management, FCF table management, VFI/VPI/FCFI registration, read configuration/revision, feature request/set, object read/write, congestion buffer registration, diagnostics, host data, trunking, and RAS firmware logging. Mailbox completion is represented by `struct lpfc_mcqe`.

DMA and data path descriptors include `struct ulp_bde64`, `struct ulp_bde64_le`, `struct lpfc_bde4`, `struct sli4_sge`, `struct sli4_sge_le`, `struct sli4_hybrid_sgl`, `struct fcp_cmd_rsp_buf`, and `struct sli4_sge_diseed`. These cover host- and port-resident BDEs, immediate BDEs, SGL entries, DIF/DISEED metadata, encrypted or protection-related SGE types, SGL alignment, and command/response buffer DMA state.

FCoE and fabric discovery structures include `struct fcf_record`, `struct lpfc_mbx_read_fcf_tbl`, `struct lpfc_mbx_add_fcf_tbl_entry`, `struct lpfc_mbx_del_fcf_tbl_entry`, `struct lpfc_mbx_redisc_fcf_tbl`, `struct lpfc_mbx_reg_fcfi`, and `struct lpfc_mbx_reg_fcfi_mrq`. These encode FCF records, MAC/fabric/switch names, VLAN bitmap data, queue routing, multi-receive-queue policy, and FCFI registration filters.

Feature, capability, and diagnostic structures include `struct lpfc_sli4_parameters`, `struct lpfc_mbx_request_features`, `struct lpfc_mbx_set_feature`, `struct lpfc_mbx_read_config`, `struct lpfc_mbx_read_rev`, `struct lpfc_mbx_memory_dump_type3`, SFF-8472 transceiver EEPROM layouts, `struct lpfc_rsrc_desc_pcie`, `struct lpfc_rsrc_desc_fcfcoe`, `struct lpfc_func_cfg`, `struct lpfc_prof_cfg`, and `struct lpfc_controller_attribute`.

Async completion queue events are represented by `struct lpfc_acqe_link`, `struct lpfc_acqe_fip`, `struct lpfc_acqe_dcbx`, `struct lpfc_acqe_grp5`, `struct lpfc_acqe_fc_la`, `struct lpfc_acqe_misconfigured_event`, `struct lpfc_acqe_cgn_signal`, and `struct lpfc_acqe_sli`. These are used to decode link, FIP, DCBX, FC link attention, SLI, misconfiguration, congestion, and diagnostic events.

The WQE section defines the transmit/IO command surface:

- Common fields: `struct wqe_common`, `struct wqe_did`, `struct wqe_rctl_dfctl`, and command type constants.
- ELS/BLS/FCP/NVMe/Congestion WQEs: `struct els_request64_wqe`, `struct xmit_els_rsp64_wqe`, `struct xmit_bls_rsp64_wqe`, `struct xmit_seq64_wqe`, `struct xmit_bcast64_wqe`, `struct gen_req64_wqe`, `struct lpfc_nvme_prli`, `struct create_xri_wqe`, `struct cmf_sync_wqe`, `struct abort_cmd_wqe`, `struct fcp_iwrite64_wqe`, `struct fcp_iread64_wqe`, `struct fcp_icmnd64_wqe`, `struct fcp_trsp64_wqe`, `struct fcp_tsend64_wqe`, `struct fcp_treceive64_wqe`, and `struct send_frame_wqe`.
- `union lpfc_wqe` and `union lpfc_wqe128` provide 64-byte and 128-byte overlays used by IO paths.

## Control Flow and Integration

This header does not implement runtime control flow directly. Its control-flow impact is declarative: it determines how LPFC code builds mailbox commands, posts work queue entries, rings doorbells, decodes completions, and branches on hardware status fields.

Typical integration flow is:

1. Probe and initialization code reads SLI interface and ASIC identity registers using `lpfc_sli_intf`, `lpfc_asic_id`, register offsets, and `bf_get` fields.
2. Mailbox setup code fills `struct lpfc_mqe` overlays for queue creation, feature negotiation, SGL page posting, VFI/VPI/FCFI registration, and SLI parameter discovery.
3. Queue setup code creates EQ/CQ/MQ/WQ/RQ contexts and writes doorbell registers described by this file.
4. IO submission paths fill `union lpfc_wqe128` or `union lpfc_wqe` with FCP, ELS, BLS, NVMe, or generic request fields, then post entries to WQs.
5. Interrupt and polling paths decode EQE/CQE/WCQE/RCQE/ACQE structures, status codes, valid bits, request tags, XRI tags, event trailers, and async event payloads to complete jobs or update link/fabric state.

Cross-reference scanning confirms heavy use of `bf_get` and `bf_set` against this header in `lpfc_sli.c`, `lpfc_hbadisc.c`, `lpfc_els.c`, and other driver files. `lpfc_bsg.h` duplicates related bitfield helper concepts for user/kernel BSG ABI exposure because this kernel-only header is not directly accessible to userspace.

## State and Persistence Behavior

The file stores no software state by itself. It defines transient in-memory representations of hardware-visible state:

- Queue state is carried by queue entries, valid bits, queue IDs, completion queue IDs, request tags, XRI/RPI/VPI/VFI/FCFI identifiers, and doorbell release/post counts.
- Adapter configuration and negotiated capabilities are conveyed through mailbox request/response payloads such as `lpfc_mbx_read_config`, `lpfc_mbx_get_sli4_parameters`, `lpfc_mbx_request_features`, and `lpfc_mbx_set_feature`.
- Fabric state is represented through FCF records, FCFI registrations, VFI/VPI registration payloads, link events, and async event tags.
- Persistent device-side changes are possible through mailbox objects and features, notably `lpfc_mbx_wr_object`, firmware object read/write, set boot/config/profile commands, beacon/trunk/host-data settings, RAS firmware logging, and feature toggles. The header only describes those payloads; persistence semantics are implemented by firmware and caller code.

Because these structures map to DMA rings, BAR registers, and firmware command formats, layout stability is part of the driver/device ABI. Packing, endianness, word numbering, and reserved bits are effectively persistent compatibility constraints across firmware generations.

## Dependencies and External Contracts

The header depends on Fibre Channel protocol structures for RDF/FPIN support and on LPFC legacy definitions from surrounding headers for command constants, PCI IDs, FCP structures, and bit definitions. Hardware and firmware dependencies are stronger than C dependencies: every field definition must match SLI-4 specifications for supported ASIC generations, queue versions, and mailbox opcode versions.

Important integration points include:

- PCI probe path and hardware setup in `lpfc_init.c`.
- Mailbox assembly and completion handling in `lpfc_mbox.c` and `lpfc_sli.c`.
- FCP command templates and IO submission in `lpfc_scsi.c`.
- NVMe initiator and target data paths in `lpfc_nvme.c` and `lpfc_nvmet.c`.
- Fabric discovery and FCF/VFI/VPI handling in `lpfc_hbadisc.c`.
- ELS/BLS request and response handling in `lpfc_els.c` and `lpfc_sli.c`.
- Debug, BSG, attribute, and diagnostics surfaces that expose or decode hardware state.

## Risks

The main risk is ABI drift. A wrong shift, mask, word index, queue size, mailbox payload layout, opcode, status code, or endian annotation can cause silent hardware misprogramming, DMA corruption, lost completions, link bring-up failures, bad resource accounting, or firmware rejection.

Bitfield helper misuse is another high-risk area. `bf_set` preserves existing bits in a word, so uninitialized words can leak stale fields unless callers zero structures first. Native-endian helpers must not be used on little- or big-endian wire fields that require conversion. Some field names are reused across versioned request/response unions, so callers must select the correct version and overlay.

The file contains overlapping and version-specific fields, especially in WQE common words, queue context formats, RQ/WQ create variants, FCFI MRQ fields, and feature payloads. Adding support for new firmware or ASIC families must avoid breaking older formats. The typo-like symbol `lpfc_mbx_rq_ftr_rsp_vf__MASK` is part of a field triplet anomaly and should be treated carefully before any cleanup, because callers may or may not depend on the exact macro name.

SFF/transceiver and firmware-object layouts contain large fixed-size buffers. Bad length validation in callers could produce overreads, partial data interpretation, or firmware object write errors. `struct user_eeprom` in particular has a very large `vendor_pn` array, so assumptions about field sizes should be validated against the relevant SFF table and caller expectations.

## Test Signals

Useful validation signals for changes touching this header include:

- Compile coverage for every LPFC object that includes `lpfc_hw4.h`; field triplet errors usually surface as build failures where `bf_get`/`bf_set` is used.
- PCI probe and SLI-4 initialization on representative if_type 0, 2, and 6 adapters, including G6/G7/G7P/G8 families.
- Queue creation/destruction tests for EQ, CQ, MQ, WQ, RQ, including versioned queue create paths and if_type 6 doorbells.
- Mailbox command tests for read config, read revision, get SLI4 parameters, request/set features, post SGL pages, register/unregister VFI/VPI/FCFI, and read/write object flows.
- IO path tests for FCP read/write/command, ELS request/response, BLS response, abort, send-frame, NVMe PRLI, and congestion-management WQEs.
- Error-path tests for CQE status decoding, XRI aborted completions, receive completions, mailbox status/additional status handling, FCF table empty/in-use states, and unsupported firmware features.
- Link and async event tests for FC link attention, FIP events, SLI events, congestion events, misconfigured port events, trunking, and transceiver diagnostics.
