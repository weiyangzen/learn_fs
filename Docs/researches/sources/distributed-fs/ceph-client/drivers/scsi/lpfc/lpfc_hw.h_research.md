# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_hw.h

## Purpose
`lpfc_hw.h` is the SLI-2/SLI-3 hardware and Fibre Channel protocol contract for the Broadcom/Emulex `lpfc` driver. It defines well-known Fibre Channel IDs, CT name-server and FDMI payloads, ELS payloads, service parameters, SLI mailbox commands, IOCB command layouts, DMA buffer descriptors, Host Buffer Queue entries, register bits, PCI device IDs, and the SLI-2 shared-memory layout used by firmware and the driver.

The file is mostly ABI: structures are written into DMA buffers, SLIM memory, mailbox queues, IOCB rings, or wire-format payloads. The rest of the driver builds commands by filling these definitions rather than by using opaque helper objects.

## Important APIs, Types, And Functions
The top-level protocol constants define fabric and well-known D_ID values such as `NameServer_DID`, `Fabric_DID`, `FDMI_DID`, ring numbers `LPFC_FCP_RING`, `LPFC_EXTRA_RING`, `LPFC_ELS_RING`, default timeouts, IOCB ring sizes, and SLI-2/3 IOCB sizes.

`struct lpfc_sli_ct_request` is the common CT request/response frame. Its union covers name-server requests such as `GID_FT`, `RFT_ID`, `RNN_ID`, `RSPN_ID`, `RFF_ID`, `GFF_ID`, `GFT_ID`, FDMI/MIB preamble reuse, and VMID application-server payload offsets. The associated `SLI_CT*`, `SLI_CTNS_*`, `SLI_MGMT_*`, FDMI attribute, and VMID constants drive `lpfc_ct.c` and BSG CT passthrough handling.

`struct lpfc_name`, `struct csp`, `struct class_parms`, `struct serv_parm`, and `struct aux_parm` model login service parameters exchanged in FLOGI/PLOGI/FDISC and mailbox service-parameter commands.

The ELS section defines `ELS_CMD_*` opcodes and payload structures including `LOGO`, `PRLI`, `PRLO`, `ADISC`, `FAN`, `SCR`, `RNID`, `RLS`, `RRQ`, `RTV_RSP`, `RPL`, `ELS_PKT`, LCB beacon frames, RDP request/response descriptors, QFPA/UVEM frames, and FPIN/EDC opcode aliases from `<uapi/scsi/fc/fc_els.h>`.

The mailbox ABI starts with register and attention bits (`FF_REGS`, `HA_*`, `CA_*`, `HS_*`, `HC_*`) and command codes (`MBX_*`). `MAILBOX_t` combines the owner/status/command word, the `MAILVARIANTS` union of command-specific payloads, and SLI-2/3 host/port group pointer overlays. Important payloads include `INIT_LINK_VAR`, `CONFIG_RING_VAR`, `READ_CONFIG_VAR`, `READ_SPARM_VAR`, `READ_STATUS_VAR`, `READ_RPI_VAR`, `READ_REV_VAR`, `READ_LNK_VAR`, `REG_LOGIN_VAR`, `REG_VPI_VAR`, `UNREG_VPI_VAR`, `DUMP_VAR`, `config_hbq_var`, `CONFIG_PORT_VAR`, and `config_msi_var`.

The DMA and IOCB ABI centers on `struct ulp_bde`, `ULP_BDL`, `struct ulp_bde64` from `lpfc_hw4.h`, BlockGuard PDE descriptors, `PARM_ERR`, `WORD5`, IOCB command templates such as `ELS_REQUEST64`, `GEN_REQUEST64`, `FCPI_FIELDS64`, `RCV_ELS_REQ64`, `ASYNCSTAT_FIELDS`, `QUE_XRI64_CX_FIELDS`, `struct fcp_irw_ext`, and the final `IOCB_t` union. The inline `lpfc_bgs_get_*()` helpers decode BlockGuard status word bits, and `lpfc_is_LC_HBA()` selects legacy adapter-specific initialization by PCI device ID.

`PCB_t`, `SLI2_RDSC`, `struct lpfc_hgp`, `struct lpfc_pgp`, `union sli_var`, and `struct lpfc_sli2_slim` define the shared SLI-2 memory image containing mailbox space, mailbox extension words, the port control block, and IOCB storage.

## Control Flow
This header does not own runtime control flow, but it shapes several major flows.

During SLI-2/3 initialization, `lpfc_init.c` maps SLIM memory and sets `phba->mbox`, `phba->mbox_ext`, `phba->pcb`, and `phba->IOCBs` using `offsetof(struct lpfc_sli2_slim, ...)`. `lpfc_mbox.c` then builds `MBX_CONFIG_PORT` with `CONFIG_PORT_VAR`, fills `PCB_t` ring descriptors, mailbox pointers, HGP/PGP pointers, optional HBQ/BlockGuard/NPIV feature requests, and swaps PCI-visible memory as needed.

Mailbox builders zero an `LPFC_MBOXQ_t`, select a `MBX_*` opcode, fill the matching `MAILVARIANTS` member, set `mbxOwner = OWN_HOST`, and submit it. Completion status returns through `mbxStatus` and command-specific union fields. Examples include link bring-up/down, `READ_REV`, `READ_CONFIG`, `READ_TOPOLOGY`, `CONFIG_RING`, `CONFIG_HBQ`, `REG_LOGIN64`, `REG_VPI`, and dump/read-log commands.

IOCB flow is ring based. `lpfc_sli.c` indexes command and response rings by `phba->iocb_cmd_size` and `phba->iocb_rsp_size`, which are selected from the SLI-2/3 constants in this header. ELS, CT, and FCP paths fill `IOCB_t` overlays, BDE/BDL fields, context tags, class, command opcode, owner, timeout, and BDE count, then issue the IOCB to firmware. Completion paths read `ulpStatus`, `PARM_ERR`, `WORD5`, and command-specific overlays.

Receive-buffer flow uses `CMD_QUE_RING_BUF64_CN`, `struct lpfc_hbq_entry`, and `config_hbq_var`: initialization posts ELS/CT buffers, HBQ setup binds R_CTL/TYPE masks and selection profiles to rings, and unsolicited CT/ELS handling consumes the BDEs and payload structures defined here.

FCP SCSI flow preallocates per-command `IOCB_t` instances and BPL memory. Queuecommand setup fills `struct ulp_bde64` entries for FCP command, response, and data scatter-gather segments, optionally using the SLI-3 extended IOCB `fcp_irw_ext` inline BDEs and BlockGuard fields.

## State, Persistence, And Dependencies
The header defines no persistent state by itself. Its structures describe state persisted in adapter firmware, SLIM memory, DMA buffers, port login tables, vport/vfi/vpi/rpi/xri resource maps, and Fibre Channel fabric services.

The most important state boundary is ownership. `OWN_HOST` and `OWN_CHIP` transfer mailbox and IOCB entries between driver and firmware. `mbxStatus`, `ulpStatus`, mailbox command responses, ring put/get pointers, HBQ pointers, and RPI/VPI/VFI identifiers are the state that survives across asynchronous command issue and completion.

The definitions depend on Linux kernel integer types, endian annotations, bitfield configuration macros (`__BIG_ENDIAN_BITFIELD` and little-endian alternatives), PCI constants, SCSI netlink vendor IDs, Fibre Channel UAPI ELS definitions, and `lpfc_hw4.h` for shared BDE/BLS structures. Many fields are explicitly big-endian wire-format values while PCI/SLIM ring pointers use little-endian or firmware-specific byte swapping.

## Integration Points
`lpfc_mbox.c` is the primary consumer of `MAILBOX_t`, `PCB_t`, `CONFIG_PORT_VAR`, `config_hbq_var`, and most `MBX_*` command-specific payloads.

`lpfc_sli.c` consumes `IOCB_t`, IOCB command constants, owner bits, BDE/BDL layouts, ring pointer structures, and SLI-2/3 IOCB sizing when issuing, completing, and aborting commands.

`lpfc_ct.c` and `lpfc_bsg.c` use `struct lpfc_sli_ct_request`, CT command/response codes, `LPFC_CT_PREAMBLE`, FDMI/MI/VMID constants, and BDE lists for fabric name-server, FDMI, MIB, and userspace BSG CT operations.

`lpfc_els.c`, discovery, and nport state code use ELS opcodes and payload structs for login, logout, PRLI/PRLO, RSCN, SCR, RDP diagnostics, RRQ, RTV, beacon, FPIN/EDC, and peer response generation.

`lpfc_scsi.c`, `lpfc_nvme.c`, and `lpfc_nvmet.c` use `struct ulp_bde64`, `IOCB_t`, FCP IOCB overlays, class/status constants, and BlockGuard decoding for SCSI FCP and NVMe/F target data paths.

`lpfc_init.c`, `lpfc_mem.c`, debugfs, and sysfs/BSG mailbox paths rely on the SLIM layout, mailbox sizes, extended mailbox area, PCI device IDs, interrupt attention bits, and adapter capability constants.

## Risks
This file is an ABI surface. Any field reorder, size change, padding change, endian mistake, or bitfield direction mistake can break hardware command submission or corrupt Fibre Channel wire payloads. The risk is highest in `MAILBOX_t`, `IOCB_t`, `PCB_t`, `struct lpfc_sli_ct_request`, service parameters, and RDP/FDMI descriptors.

C bitfields are used extensively for hardware words. They depend on the kernel endian configuration and on callers using the right CPU-to-device or CPU-to-wire conversion. Mixed patterns such as big-endian CT/ELS payloads, little-endian BDE words, and PCI memory copies make accidental double-swapping or missing swapping plausible.

Several structures overlay different command formats in unions. Reused IOCB and mailbox objects must be fully zeroed and the correct union member must match the command opcode. Stale `ulpBdeCount`, `ebde_count`, owner, context, VPI/RPI, or BDE flags can cause firmware rejects, DMA to the wrong address, or leaked receive buffers.

DMA length and count fields are hardware-visible. Incorrect `bdeSize`, BPL length, immediate-data offsets, HBQ entry counts, mailbox extension sizes, or `MAX_SLIM_IOCB_SIZE` assumptions can lead to truncated transfers, out-of-bounds firmware access, or completion errors that appear far from the setup site.

Protocol constants are shared across fabric services, SCSI, NVMe, and management paths. Adding support for new ELS/CT/FDMI features without matching response parsing, rejection behavior, and userspace BSG validation can create interoperability regressions.

## Test Signals
Build-time signals include compile failures from structure definitions, missing constants, endian annotations, and `offsetof()` expressions used by mailbox and SLIM setup.

Driver initialization should validate that `MBX_READ_REV`, `MBX_CONFIG_PORT`, `MBX_CONFIG_RING`, `MBX_CONFIG_HBQ`, `MBX_READ_CONFIG`, and `MBX_READ_TOPOLOGY` complete successfully, that IOCB ring sizes match the selected SLI revision, and that HGP/PGP pointers advance without mailbox timeouts or adapter error attention bits.

Discovery and fabric-service tests should exercise FLOGI/PLOGI/PRLI/LOGO/SCR/RSCN, CT name-server registration/query, FDMI registration, and unsupported CT/MI rejection paths. Strong failure signals are LS_RJT/FS_RJT reason mismatches, invalid D_ID/RPI/VPI errors, stuck ELS ring events, or repeated `IOSTAT_LOCAL_REJECT` with `IOERR_INVALID_RPI`, `IOERR_ILLEGAL_FIELD`, or `IOERR_BAD_HOST_ADDRESS`.

I/O tests should cover SLI-3 immediate FCP command mode, BPL fallback for more than three data BDEs, BlockGuard/DIF paths, abort/close XRI paths, and large scatter-gather requests. Watch for DMA mapping errors, unexpected `IOSTAT_FCP_RSP_ERROR`, BlockGuard status bits decoded by `lpfc_bgs_get_*()`, and completions with stale or impossible transfer lengths.

Management and diagnostic tests should cover RDP descriptor responses, link statistics, event-log reads, static vport dumps, beacon commands, and BSG raw mailbox/CT passthrough. These paths expose mailbox extension sizing, BDE formatting, and wire-format descriptor length bugs.
