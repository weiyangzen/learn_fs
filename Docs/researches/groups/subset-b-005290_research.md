# Research: subset-b-005290

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_hw4.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_hw4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_ids.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_ids.h

## Purpose

`lpfc_ids.h` defines the LPFC driver's PCI device ID table, `lpfc_id_table`. This table is the match list used by the Linux PCI core to bind the LPFC driver to supported Emulex/Broadcom, ServerEngines, and ATTO Fibre Channel adapters. It is intentionally data-only: the file includes `<linux/pci.h>` and initializes an array of `const struct pci_device_id` entries terminated by `{ 0 }`.

The table is included by `lpfc_init.c`, where it is exported through `MODULE_DEVICE_TABLE(pci, lpfc_id_table)` and assigned to the driver's `struct pci_driver` `.id_table`. This makes the table both a runtime probe contract and a module autoload alias source.

## Important APIs, Types, and Constants

The only exported object in this header is:

- `const struct pci_device_id lpfc_id_table[]`

Each entry contains vendor ID, device ID, subsystem vendor ID, and subsystem device ID fields. Most Emulex/Broadcom and ServerEngines entries use `PCI_ANY_ID` for subsystem fields, allowing the driver to bind across board variants. ATTO entries are more specific: they use ATTO vendor/device pairs with specific subsystem IDs to distinguish Celerity and ThunderLink models.

The table covers older Emulex adapters such as Viper, Firefly, Thor, Pegasus, Centaur, Dragonfly, Superfly, RFLY, PFLY, Neptune variants, Helios variants, BMID/BSMB, Zephyr variants, TFLY, LP101/LP10000S/LP11000S/LPE11000S, Saturn variants, Proteus variants, Falcon, Balius, Lancer FC/FCoE physical and VF devices, Lancer G6/G7/G7P/G8 FC, and Skyhawk physical/VF devices. It also includes ServerEngines Tigershark and Tomcat IDs and ATTO Celerity/ThunderLink combinations.

The numeric `PCI_VENDOR_ID_*` and `PCI_DEVICE_ID_*` constants are not defined here. In this source tree they are available from LPFC hardware definitions such as `lpfc_hw.h` and standard kernel PCI headers.

## Control Flow and Integration

The control flow enabled by this file is Linux PCI driver binding:

1. The PCI core enumerates a device and compares vendor/device/subsystem IDs against `lpfc_id_table`.
2. If an entry matches, the LPFC `pci_driver` in `lpfc_init.c` can probe the device.
3. `MODULE_DEVICE_TABLE` causes module alias metadata to be generated so supported devices can autoload the module.
4. Once probe runs, later LPFC initialization code uses the matched PCI IDs and additional hardware discovery to select generation-specific behavior, ATTO labeling, SLI mode, FC/FCoE handling, VF/PF handling, and feature support.

Cross references show `lpfc_init.c` includes this header and registers the table at the bottom of the driver definition. Other initialization code switches on several IDs listed here, especially ATTO subsystem IDs and modern Lancer/Skyhawk/Proteus IDs, to adjust adapter type naming and behavior.

## State and Persistence Behavior

The table is static const module data. It has no runtime mutation and no persistence side effects. Its persistent impact is in kernel module metadata and boot-time device binding: adding or removing an entry changes which PCI devices can autoload and bind to the LPFC driver across reboots.

Because several entries use `PCI_ANY_ID` for subsystem matching, their binding scope is broad. The ATTO entries use subsystem-specific matches, which makes their binding behavior more constrained and dependent on exact subsystem IDs.

## Dependencies and External Contracts

The file depends on `<linux/pci.h>` for `struct pci_device_id` and `PCI_ANY_ID`. It depends on the LPFC build including definitions for all `PCI_VENDOR_ID_*` and `PCI_DEVICE_ID_*` symbols before or around inclusion. Its primary integration points are:

- `lpfc_init.c` include of `lpfc_ids.h`.
- `MODULE_DEVICE_TABLE(pci, lpfc_id_table)` module alias generation.
- `struct pci_driver` registration with `.id_table = lpfc_id_table`.
- Device-specific probe logic in `lpfc_init.c`, `lpfc_attr.c`, and related code paths that switch on IDs from the table.

## Risks

Incorrect entries have immediate hardware support consequences. A missing ID prevents supported adapters from probing or autoloading. A too-broad ID can bind LPFC to an unsupported or vendor-customized device. A wrong subsystem tuple can break ATTO-specific matching or cause a generic path to claim a branded adapter that needs special naming or behavior.

Because the file defines a non-`static` const object in a header, it must be included in exactly the intended translation unit. Including it from multiple C files would create duplicate definitions at link time. The current tree uses it from `lpfc_init.c`, which matches that pattern.

Ordering can matter for human maintenance and for overlapping ATTO device/subsystem combinations. The terminator `{ 0 }` is required; omitting or moving it would allow the PCI core to read beyond the table.

## Test Signals

Useful validation signals for changes touching this file include:

- Successful LPFC module build and link, confirming the table is defined once and all PCI ID constants resolve.
- `modinfo` or generated module alias checks showing expected PCI aliases for new or changed devices.
- Probe tests, or at least PCI modalias matching tests, for Emulex/Broadcom, ServerEngines, and ATTO IDs.
- Negative matching tests for nearby unsupported subsystem IDs, especially ATTO variants.
- Runtime probe smoke tests that confirm `lpfc_init.c` still maps matched IDs to the correct adapter type, generation, VF/PF handling, and FC/FCoE behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_ids.h -->
