# Group Research: group_580_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__deb7fa77ccf4

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_iocb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_iocb.h

## Purpose

Defines IOCB command opcodes, status/error encodings, and in-memory command/completion overlays for the Emulex `emlxs` Fibre Channel adapter driver. It covers legacy SLI-1/2/3 IOCB formats and bridges to SLI4 by embedding an `emlxs_wqe_t` in `emlxs_iocbq_t`.

## Main Definitions

- IOCB command constants for receive, transmit, ELS, abort/close XRI, FCP initiator, FCP target mode, adapter events, LP3000 BPL commands, SLI2 64-bit commands, SLI3 receive commands, and generic request/list commands.
- `PARM_ERR`: packed local/remote reject status detail fields with codes for fabric busy, port busy, LS_RJT, BA_RJT, and driver-local IO errors.
- `WORD5`: overlay for frame header control/status fields: `Rctl`, `Type`, `Dfctl`, `Fctl`.
- IOCB payload templates:
  - `GENERIC_RSP`
  - `XR_SEQ_FIELDS`
  - `ELS_REQUEST`
  - `RCV_ELS_REQ`
  - `AC_XRI`
  - `GET_RPI`
  - `FCPI_FIELDS`
  - `FCPT_FIELDS`
  - 64-bit variants such as `XMT_SEQ_FIELDS64`, `RCV_SEQ_FIELDS64`, `ELS_REQUEST64`, `RCV_ELS_REQ64`, `FCPI_FIELDS64`, `FCPT_FIELDS64`
  - `AUTO_TRSP`
  - `GENERIC_EXT_IOCB`
  - `RCV_SEQ_ELS_64_SLI3_EXT`
- `emlxs_iocb_t`: volatile 128-byte IOCB format with command-specific union, `ulpContext`/`ulpIoTag` overlays, command/status/owner bitfields, and SLI3 extension area.
- `emlxs_iocbq_t`: driver queue wrapper containing the IOCB, SLI4 WQE, linkage, back-pointers to buffers/port/channel/node/pkt, and flags.

## Integration Notes

This header is a hardware ABI surface. It depends on types defined elsewhere in the driver stack, including `ULP_BDE`, `ULP_BDE64`, `ULP_BDL`, `emlxs_wqe_t`, and driver private objects referenced through `void *` back-pointers.

The `emlxs_iocbq_t` wrapper is the object likely passed through driver queues; it binds the raw IOCB/WQE to software ownership and completion context.

## Risks and Gotchas

- Almost every packed control word has separate `EMLXS_BIG_ENDIAN` and `EMLXS_LITTLE_ENDIAN` layouts. Any include-order or platform macro error changes hardware-visible bit positions.
- Command numeric values intentionally overlap across SLI generations and contexts; consumers must interpret them with SLI mode and command path.
- The IOCB structure aliases fields through macros such as `ULPCONTEXT`, `ULPIOTAG`, `ULPCOMMAND`, `ULPSTATUS`, `RXFCHDR`, `RXSEQCNT`, and `RXSEQLEN`; refactoring should preserve exact offsets.
- Target-mode commands are present but conditional at use sites, not in this header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_iocb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mbox.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mbox.h

## Purpose

Defines the mailbox command ABI for Emulex adapters across SLI2/3 and SLI4. This is the largest protocol header in the group: it includes mailbox command/status constants, per-command payload layouts, SLI port control blocks, SLI4 IOCTL mailbox requests, queue creation contexts, FCoE/FCF management records, and firmware download/load-list structures.

## Main Definition Areas

### Mailbox Commands and Status

Defines `MBX_*` opcodes from basic lifecycle commands (`MBX_INIT_LINK`, `MBX_DOWN_LINK`, `MBX_CONFIG_LINK`) through discovery/status (`MBX_READ_CONFIG`, `MBX_READ_REV`, `MBX_READ_LA`), login/resource management (`MBX_REG_LOGIN`, `MBX_UNREG_RPI`, `MBX_REG_VPI`, `MBX_REG_VFI`, `MBX_REG_FCFI`), diagnostics, firmware loading, event logging, and SLI4 `MBX_SLI_CONFIG`.

Status constants include firmware/adapter errors (`MBXERR_*`) and driver-side pseudo-statuses (`MBX_BUSY`, `MBX_TIMEOUT`, `MBX_NOT_FINISHED`, `MBX_HARDWARE_ERROR`). Issue modes include `MBX_POLL`, `MBX_SLEEP`, `MBX_WAIT`, `MBX_NOWAIT`, and `MBX_BOOTSTRAP`.

### SLI2/3 Mailbox Payloads

Defines many mailbox payload structs, including:

- Firmware/program identity and compatibility: `REVCOMPAT`, `PROG_ID`, `LOAD_SM_VAR`, `LOAD_AREA_VAR`, `LOAD_EXP_ROM_VAR`.
- Link configuration and status: `INIT_LINK_VAR`, `CONFIG_LINK`, `READ_CONFIG_VAR`, `READ_CONFIG4_VAR`, `READ_LNK_VAR`, `READ_LA_VAR`, `CLEAR_LA_VAR`.
- Ring and HBQ configuration: `PART_SLIM_VAR`, `CONFIG_RING_VAR`, `READ_RCONF_VAR`, `HBQE_t`, `HBQ_INIT_t`, `CONFIG_HBQ_VAR`.
- Service parameters and login state: `READ_SPARM_VAR`, `READ_RPI_VAR`, `READ_XRI_VAR`, `REG_LOGIN_VAR`, `UNREG_LOGIN_VAR`, `REG_WD30`.
- NPIV/FCoE fabric identity: `REG_VPI_VAR`, `INIT_VPI_VAR`, `UNREG_VPI_VAR`, `UNREG_VPI_VAR4`, `REG_VFI_VAR`, `INIT_VFI_VAR`, `UNREG_VFI_VAR`, `REG_FCFI_VAR`, `UNREG_FCFI_VAR`, `RESUME_RPI_VAR`.
- Diagnostics and dumps: `BIU_DIAG_VAR`, `DUMP_VAR`, `DUMP4_VAR`, `READ_EVT_LOG_VAR`, `LOG_STATUS_VAR`.
- Port/config feature negotiation: `CONFIG_PORT_VAR`, `REQUEST_FEATURES_VAR`.

`MAILVARIANTS` is the union for SLI2/3 mailbox command overlays, and `MAILBOX` is the 256-byte volatile mailbox format including status/command/owner fields plus SLI pointer state.

### SLI4 IOCTL Mailbox Layer

Defines the SLI4 management request envelope:

- `mbox_req_hdr_t`
- `mbox_req_hdr2_t`
- `mbox_rsp_hdr_t`
- `be_req_hdr_t`
- `SLI_CONFIG_VAR`
- `MAILVARIANTS4`
- `MAILBOX4`

The IOCTL layer defines subsystem and opcode constants for common, low-level, FCoE, and DCBX operations. It includes flash operations, object read/write/list/delete, boot config, firmware config query, physical link config, extents, SLI4 parameters, queue creation, FCF table management, and DCBX mode get/set.

### Queue Creation Contexts

The file declares SLI4 queue context structures used by mailbox create commands:

- `EQ_CONTEXT`
- `CQ_CONTEXT`
- `CQ_CONTEXT_V2`
- `MQ_CONTEXT`
- `MQ_CONTEXT_V1`
- `RQ_CONTEXT`
- `RQ_CONTEXT_V1`

Associated request wrappers include `IOCTL_COMMON_EQ_CREATE`, `IOCTL_COMMON_CQ_CREATE`, `IOCTL_COMMON_CQ_CREATE_V2`, `IOCTL_COMMON_MQ_CREATE`, `IOCTL_COMMON_MQ_CREATE_EXT`, `IOCTL_COMMON_MQ_CREATE_EXT_V1`, `IOCTL_FCOE_RQ_CREATE`, `IOCTL_FCOE_RQ_CREATE_V1`, `IOCTL_FCOE_WQ_CREATE`, and `IOCTL_FCOE_WQ_CREATE_V1`.

### FCoE and Management Structures

Defines FCoE/FCF management records and operations:

- `FCF_RECORD_t`
- `IOCTL_FCOE_READ_FCF_TABLE`
- `IOCTL_FCOE_ADD_FCF_TABLE`
- `IOCTL_FCOE_DELETE_FCF_TABLE`
- `IOCTL_FCOE_REDISCOVER_FCF_TABLE`
- `IOCTL_FCOE_CFG_POST_SGL_PAGES`
- `IOCTL_FCOE_POST_HDR_TEMPLATES`
- `MGMT_HBA_ATTRIB`
- `MGMT_CONTROLLER_ATTRIB`
- `IOCTL_COMMON_GET_CNTL_ATTRIB`

### Firmware Image and Flash Layout

At the end, the file defines flash/download constants, image addresses, `AIF_HDR`, `IMAGE_HDR`, `WAKE_UP_PARMS`, `LOAD_ENTRY`, and `LOAD_LIST`. These model firmware area IDs, erase/download/copy state machines, and load-list entries.

## Integration Notes

This header is central to adapter bring-up, firmware management, mailbox command submission, SLI4 queue setup, FCoE discovery, and NPIV/fabric resource management. It depends on many driver and Fibre Channel types defined elsewhere, including `ULP_BDE`, `ULP_BDE64`, `MATCHMAP`, `BE_PHYS_ADDR`, `NAME_TYPE`, `emlxs_ring_def_t`, `emlxs_rings_t`, `MAX_RINGS_AVAILABLE`, `SLI_SLIM1_SIZE`, `SLI_IOCB_MAX_SIZE`, and related SLI definitions.

`emlxs_mbq_t` is the software mailbox queue wrapper. It stores the raw mailbox words, queue linkage, deferred completion context pointers, flags, optional extension buffer, and completion callback.

## Risks and Gotchas

- This is an ABI header. Layout changes can break firmware/hardware communication.
- Endian-specific bitfields are pervasive and must remain synchronized.
- Several opcodes intentionally share numeric values across SLI generations, for example SLI2/3 `MBX_UNREG_LOGIN` and SLI4 `MBX_UNREG_RPI`.
- Many variable-length command shapes use one-element arrays or integer fields that represent trailing payloads or DMA buffers; bounds checking must live in command construction code.
- `MBOX_EXT_SUPPORT` changes mailbox extension sizing and `emlxs_mbq_t` fields.
- Some fields are comments-as-contract, such as page counts, object name word spans, and flash offsets; there is little type-level enforcement.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mbox.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mdb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mdb.h

## Purpose

Declares MDB debugger support for the `emlxs` driver.

## Main Definitions

- `DRIVER_NAME` is set to `"emlxs"`.
- Includes MDB and DDI kernel headers: `sys/mdb_modapi.h`, `sys/ddi.h`, `sys/sunddi.h`, plus `kmem` and basic types.
- `MAX_FC_BRDS` is defined as `256`.
- Declares help and dcmd entry points:
  - `void emlxs_msgbuf_help();`
  - `int emlxs_msgbuf(uintptr_t base_addr, uint_t flags, int argc, const mdb_arg_t *argv);`
  - `void emlxs_dump_help();`
  - `int emlxs_dump(uintptr_t base_addr, uint_t flags, int argc, const mdb_arg_t *argv);`

## Integration Notes

This is not part of the runtime adapter path. It is used by the driver’s MDB module to inspect message buffers and dumps.

## Risks and Gotchas

- Function prototypes use old-style empty parameter lists for the help functions, meaning unspecified arguments in C rather than explicit `void`.
- `MAX_FC_BRDS` duplicates the same value used in other driver headers; drift would affect debugger assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_mdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_menlo.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_menlo.h

## Purpose

Defines the Menlo management protocol used when `MENLO_SUPPORT` is enabled. Menlo appears to be a sideband/FCoE management firmware component for Emulex adapters, covering initialization, firmware download, memory access, forwarding table entries, FCoE mode/configuration, DCB/PFC priority groups, stats, logs, diagnostics, FCF/FACL state, and firmware image metadata.

## Main Definitions

### Commands

Command structures include:

- `menlo_init_cmd_t`
- `menlo_fw_download_cmd_t`
- `menlo_memory_cmd_t`
- `menlo_fte_insert_cmd_t`
- `menlo_fte_delete_cmd_t`
- `menlo_get_cmd_t`
- `menlo_set_cmd_t`
- `menlo_loopback_cmd_t`
- `menlo_reset_cmd_t`
- `menlo_fru_data_cmd_t`
- `menlo_diag_cmd_t`
- Hornet 2/FCoE extensions such as `fip_params_t`, `non_fip_params_t`, `menlo_fcoe_params_t`, `menlo_set_fcoe_params_cmd_t`, `set_facl_cmd_t`, `facl_t`, `fcf_id_t`, `create_vl_cmd_t`, `delete_vl_cmd_t`, `menlo_pg_info_t`, `menlo_set_pg_info_cmd_t`, and `menlo_set_host_eth_pfc_flag_t`.

`menlo_cmd_t` is the command union and defines command codes such as `MENLO_CMD_INITIALIZE`, `MENLO_CMD_FW_DOWNLOAD`, `MENLO_CMD_GET_CONFIG`, `MENLO_CMD_GET_PORT_STATS`, `MENLO_CMD_SET_FCOE_PARAMS`, `MENLO_CMD_GET_FCF_LIST`, `MENLO_CMD_SET_FACL`, `MENLO_CMD_CREATE_VL`, `MENLO_CMD_SET_PG`, and Zephyr-specific reset/mode commands.

### Responses

Response structures include:

- `menlo_init_rsp_t`
- `menlo_get_config_rsp_t`
- `menlo_fc_stats_rsp_t`
- `menlo_network_stats_rsp_t`
- `menlo_lif_stats_rsp_t`
- `menlo_asic_stats_rsp_t`
- `menlo_log_config_rsp_t`
- `menlo_log_data_rsp_t`
- `menlo_panic_log_data_rsp_t`
- `menlo_lb_mode_rsp_t`
- `menlo_ftable_rsp_t`
- `menlo_sfp_rsp_t`
- `menlo_fru_data_rsp_t`
- `menlo_diag_log_data_rsp_t`
- `menlo_diag_log_t`
- `menlo_diag_log_entry_t`
- Hornet 2/FCoE responses such as `menlo_get_fcoe_params_rsp_t`, `fcf_info_t`, `menlo_get_fcf_list_rsp_t`, `menlo_get_facl_rsp_t`, `create_vl_rsp_t`, `menlo_get_pg_info_rsp_t`, `menlo_get_host_eth_pfc_flag_rsp_t`, and `menlo_get_dcbx_mode_rsp_t`.

`menlo_rsp_t` is the response union and defines Menlo response/error codes including success, generic failure, invalid command/credit/size/address/context/length/type/data/value/mask/checksum, unknown FCID/WWN, busy, invalid flag, and SFP absent.

### Firmware Image Metadata

Defines:

- `menlo_image_hdr_t`
- `menlo_version_hdr_t`

These describe image length, payload length, checksum offset, padding, image type, version, and checksum.

## Integration Notes

All substantive content is guarded by `#ifdef MENLO_SUPPORT`. If that macro is not enabled, this header contributes only include guards and C++ linkage.

The protocol uses fixed-width integers for most command/response fields and many `uint32_t data` fields to represent variable trailing arrays or offsets.

## Risks and Gotchas

- Duplicate macro names such as `FCOE_MODE_NON_FIP`, `FCOE_MODE_FIP`, `SPMA_ADDR_MODE`, and `FPMA_ADDR_MODE` are defined in more than one structure block with identical meanings; edits must avoid conflicting redefinitions.
- Several response payloads expose very large stats structures; consumers must size buffers according to command response length, not just `menlo_rsp_t`.
- Log and diagnostic response structures encode trailing arrays through scalar `data` fields, so parsing code must handle variable payloads carefully.
- Menlo command and response unions are not self-validating; callers must match `code` with the correct union member.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_menlo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_messages.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_messages.h

## Purpose

Defines the driver’s message catalog and message metadata generation macros. The same header can emit extern declarations, concrete `emlxs_msg_t` objects, or a report table depending on preprocessor mode.

## Main Definitions

### Generation Modes

`DEFINE_MSG` expands differently under:

- `DEF_MSG_REPORT`: emits report entries and also includes description/action fields.
- `DEF_MSG_STRUCT`: defines `emlxs_msg_t` variables.
- default mode: declares `extern emlxs_msg_t` variables.

This lets the driver maintain one catalog while generating declarations, definitions, and documentation/report data.

### Message Groups and Masks

Defines group ranges:

- Miscellaneous: 000-099
- Driver: 100-199
- Initialization: 200-299
- Memory: 300-399
- SLI: 400-499
- Mailbox: 500-599
- Node: 600-699
- Link: 700-799
- ELS: 800-899
- Packet: 900-999
- FCP: 1000-1099
- FCT target mode: 1100-1199
- IP: 1200-1299
- SFS: 1300-1399
- IOCTL: 1400-1499
- Firmware: 1500-1599
- CT: 1600-1699
- FC-SP/DHCHAP: 1700-1799
- FCF: 1800-1899

Defines verbose masks such as `MSG_DRIVER`, `MSG_INIT`, `MSG_MEM`, `MSG_SLI`, `MSG_MBOX`, `MSG_NODE`, `MSG_LINK`, `MSG_ELS`, `MSG_PKT`, `MSG_FCP`, `MSG_FCT`, `MSG_IOCTL`, `MSG_FIRMWARE`, `MSG_CT`, `MSG_FCSP`, `MSG_FCF`, and detail masks including `MSG_MBOX_DETAIL` and `MSG_SLI_DETAIL`.

Defines levels: `EMLXS_DEBUG`, `EMLXS_NOTICE`, `EMLXS_WARNING`, `EMLXS_ERROR`, and `EMLXS_PANIC`.

### Message Type

`emlxs_msg_t` contains:

- fixed message buffer/name string
- numeric id
- level
- mask
- optional report description/action/flags under `DEF_MSG_REPORT`
- FMA ereport code pointer
- FMA impact code

### Catalog Content

The file contains the full catalog of driver messages, with entries for attach/detach/suspend/resume, initialization, memory pools, SLI/link state, mailbox completion/errors, node state, ELS send/receive/rejects, packet/FCP/IP/CT completions, diagnostics, firmware download/update/dump events, IOCTL/DFC traces, optional SFCT target-mode messages, optional DHCHAP/FC-SP messages, and FCF messages.

Several entries include FMA ereport and service-impact codes such as `DDI_FM_DEVICE_INVAL_STATE`, `DDI_FM_DEVICE_INTERN_UNCORR`, `DDI_FM_DEVICE_INTERN_CORR`, `DDI_SERVICE_LOST`, `DDI_SERVICE_DEGRADED`, and `DDI_SERVICE_UNAFFECTED`.

## Integration Notes

This header is included by `emlxs_msg.h` and by at least one compilation unit with `DEF_MSG_STRUCT` to instantiate the catalog. It relies on `emlxs_msg_t` being valid in the chosen expansion context.

Optional message entries are gated by feature macros such as `SFCT_SUPPORT` and `DHCHAP_SUPPORT`, so the available symbol set depends on build configuration.

## Risks and Gotchas

- Because the same header changes meaning based on macros, include order and one-definition discipline matter.
- FMA code constants must be available where catalog definitions are emitted.
- Message ids are grouped but not mechanically enforced by the type system.
- The catalog mixes operational logs and service-action/report text; changing strings can affect both driver diagnostics and generated reports.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_messages.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_msg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_msg.h

## Purpose

Provides message/logging support declarations for the `emlxs` driver. It includes the message catalog, defines per-source-file numeric identifiers, standard logging macros, and the in-memory circular message log structures.

## Main Definitions

- Includes `emlxs_messages.h` to expose the actual catalog declarations/definitions.
- `EMLXS_MSG_DEF(_number)` creates a static `_FILENO_` value for source files.
- File id constants map driver C files to numeric ids, including clock, diag, download, ELS, FCP, HBA, mailbox, memory, node, packet, Solaris, message, IP, thread, DFC, DHCHAP, FCT, dump, SLI3, SLI4, event, and FCF modules.
- `EMLXS_CONTEXT` expands to `port, _FILENO_, __LINE__`.
- `EMLXS_MSGF` maps to `emlxs_msg_printf`.
- `EMLXS_DEBUGF` maps to `emlxs_msg_printf` only when `EMLXS_DBG` is defined; otherwise it expands empty.
- `MAX_LOG_INFO_LENGTH` is `96`.

## Structures

`emlxs_msg_entry_t` records one log entry:

- entry id
- timestamp and high-resolution timestamp
- message pointer
- VPI, adapter instance, file number, and line number
- fixed additional-info buffer

`emlxs_msg_log_t` is the circular log:

- lock
- start time and instance
- size/count/next indices
- repeat counter
- pointer to entry buffer

## Integration Notes

This header ties message catalog entries to runtime logging. Source files likely call `EMLXS_MSG_DEF()` once, then use `EMLXS_CONTEXT` when logging.

## Risks and Gotchas

- `EMLXS_DEBUGF` expands to nothing in non-debug builds, so arguments in debug-only calls must not be required for side effects.
- The fixed 96-byte entry buffer truncates additional info unless callers handle formatting limits.
- `_FILENO_` is a static const per translation unit; duplicate ids are possible if new source files are added without updating this list.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_os.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_os.h

## Purpose

Collects OS compatibility, feature-selection macros, Solaris/illumos kernel includes, weak symbol declarations, endian selection, utility macros, unsolicited buffer structures, error translation structures, and default driver patch masks for `emlxs`.

## Main Definitions

### Feature and Platform Gates

Defines driver feature macros:

- `DHCHAP_SUPPORT`
- `SATURN_MSI_SUPPORT`
- `MENLO_SUPPORT`
- `MBOX_EXT_SUPPORT`
- `DUMP_SUPPORT`
- `SAN_DIAG_SUPPORT`
- `FMA_SUPPORT`
- `NODE_THROTTLE_SUPPORT`

For `S11`, enables `MSI_SUPPORT`, `SFCT_SUPPORT`, `MODFW_SUPPORT`, and sets `EMLXS_MODREV` to the NPIV-capable revision. `SFCT_SUPPORT` enables `MODSYM_SUPPORT` and `FCIO_SUPPORT`.

Defines `S10S11` for Solaris 10/11 compatibility and fallback `EMLXS_MODREV`/`EMLXS_MODREVX` values.

### Includes and Compatibility Constants

Includes a large set of kernel, DDI, SCSI, FMA, and Fibre Channel headers. For non-S11 builds it defines PCI/PCIe capability constants that newer headers would otherwise provide.

Defines fallback constants for FC speeds, default SID/DID, relaxed DMA ordering, taskq flags, burst sizes, and boolean values.

### Utility Macros

- `PADDR_LO`, `PADDR_HI`, `PADDR` for 64-bit physical address splitting/combining.
- `BUSYWAIT_MS`, `BUSYWAIT_US`.
- `EMLXS_MPDATA_SYNC` wrapper around `ddi_dma_sync`.
- `PKT2PRIV` and `PRIV2PKT`.
- DMA direction/status constants.
- BAR/register index constants.
- `DEAD_PTR` width-sensitive poison value.

### Unsolicited Buffer Structures

`emlxs_ub_priv_t` tracks private state for an unsolicited buffer, including FC buffer pointer, port, BPL DMA state, IP buffer DMA cookies, FC-4 type, flags, timeout, command/token, pool pointer, and linkage.

`emlxs_unsol_buf_t` tracks an unsolicited-buffer pool: pool linkage, type, buffer size, counts, flags, free/reserved counts, token range, and `fc_unsol_buf_t` array.

### Error and Table Structures

- `emlxs_xlat_err_t`: maps internal `emlxs_status` to packet state/reason/explanation/action.
- `emlxs_table_t`: generic code-to-string table entry.

### Patch Masks

Defines `EMLXS_PATCH1` through `EMLXS_PATCH32`, then names default ULP and FCP underrun patches. `DEFAULT_PATCHES` includes auto-response/ULP workarounds and residual underrun fixes.

## Integration Notes

This is an umbrella compatibility header and is likely included very early by most driver files. It controls which other headers and APIs are visible.

## Risks and Gotchas

- Feature behavior is compile-time controlled; changing one macro can alter ABI-visible structures and enabled code paths.
- Weak symbol usage allows one binary to tolerate missing platform APIs, but call sites must check availability correctly.
- `EMLXS_MPDATA_SYNC` is a multi-statement macro without `do { } while (0)`, so use in conditional contexts needs care.
- The unsolicited-buffer structures combine kernel allocation, DMA handles, token accounting, timeout state, and pool linkage; synchronization is not defined here and must be enforced by users.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_os.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_queue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_queue.h

## Purpose

Defines SLI4 queue entry formats, WQE overlays, queue sizing constants, and doorbell register layouts for the `emlxs` driver.

## Main Definitions

### Completion and Event Entries

- `EQE_t` / `EQE_u`: event queue entry with valid bit, major/minor code, and CQ id.
- CQE types:
  - `CQE_CmplWQ_t`
  - `CQE_RelWQ_t`
  - `CQE_UnsolRcv_t`
  - `CQE_UnsolRcvV1_t`
  - `CQE_XRI_Abort_t`
  - `CQE_ASYNC_t`
  - `CQE_MBOX_t`
- `CQE_u`: union over raw words and all CQE interpretations.
- Defines CQE type codes for WQ completion, release WQE, unsolicited receive, XRI aborted, and unsolicited receive V1.

### Async Event Details

Defines async FCoE, link-state, QoS, FC link attention, and port event payloads, plus constants for topology, attention type, shared link status, port fault, physical speed, event codes, FC link events, FIP events, group 5 events, and port events.

### RQ and WQE Formats

- `RQE_t`: receive queue DMA address entry.
- WQE command overlays:
  - `ELS_REQ_WQE`
  - `ELS_RSP_WQE`
  - `GEN_REQ_WQE`
  - `XMIT_SEQ_WQE`
  - `FCP_WQE`
  - `ABORT_WQE`
  - `BLS_WQE`
  - `CREATE_XRI_WQE`
- `emlxs_wqe_t`: full SLI4 WQE with command-specific first six words, context/XRI tags, timer/class/command fields, abort/request tags, CCP/performance/length/control flags, completion queue id, command type, command-specific word, and first data BDE.

Defines command type constants for FCP data in/out, target receive/response/send, generic, abort, ELS, and FIP mask. Defines ELS id constants for PLOGI/FLOGI/FDISC/LOGO/CMD.

### Queue Sizes

Defines receive buffer sizes/counts, WQE/CQE sizes, EQ/CQ/WQ/MQ/RQ depths, and max WQs per EQ.

### Doorbells

Defines packed doorbell layouts and raw-word unions for:

- `emlxs_rqdb_t` / `emlxs_rqdbu_t`
- `emlxs_wqdb_t` / `emlxs_wqdbu_t`
- `emlxs_cqdb_t`, `emlxs_cqdb6_t`, `emlxs_cqdb_u`
- `emlxs_eqdb_t`, `emlxs_eqdb6_t`, `emlxs_eqdb_u`
- `emlxs_mqdb_t` / `emlxs_mqdbu_t`

## Integration Notes

This header supplies the SLI4 data-plane queue ABI used by IOCB wrappers, mailbox queue creation, interrupt/completion processing, receive buffer posting, and work queue submission.

It depends on `ULP_BDE64` and endian macros supplied by other driver headers.

## Risks and Gotchas

- Like the mailbox and IOCB headers, this file is highly endian-sensitive.
- `WQE_PHWQ_WQID` writes into a WQE via a `uint16_t *` cast at fixed offsets. That is intentionally layout-coupled and fragile.
- Queue depth macros assume page size and element size relationships; changes must stay aligned with mailbox queue creation contexts.
- Doorbell bitfield layouts differ by interface type (`if_type 0,2` versus `if_type 6`) for CQ/EQ.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_sdapi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_sdapi.h

## Purpose

Defines the SAN Diagnostic API contract used between applications and `libdfc`, with structures and prototypes for latency collection and event registration.

## Main Definitions

### Latency Collection

- `SD_SCSI_IO_LATENCY_TYPE`
- `SD_IO_LATENCY_MAX_BUCKETS`
- `SD_time_stats_v0`
- `SD_IO_Latency_Response`
- `SD_SEARCH_LINEAR`
- `SD_SEARCH_POWER_2`

Defines return codes in `enum SD_RETURN_CODES`, including argument errors, invalid board/vport, unsupported category/subcategory/function, more data available, registration errors, memory errors, bucket not set, invalid search type, out of handles, library not initialized, and data collection active/inactive.

Declares APIs:

- `DFC_SD_Get_Granularity`
- `DFC_SD_Set_Bucket`
- `DFC_SD_Destroy_Bucket`
- `DFC_SD_Get_Bucket`
- `DFC_SD_Start_Data_Collection`
- `DFC_SD_Stop_Data_Collection`
- `DFC_SD_Reset_Data_Collection`
- `DFC_SD_Get_Data`

### Event Categories

Defines registration masks for ELS, fabric, SCSI, board, and adapter events. Defines valid subcategory masks for ELS, fabric, and SCSI event classes.

Event payload structures include:

- generic `sd_event`
- ELS wrappers and payloads: `sd_els_event_details_v0`, `sd_plogi_rcv_v0`, `sd_prlo_rcv_v0`, `sd_lsrjt_rcv_v0`, `sd_adisc_rcv_v0`
- fabric wrappers and payloads: `sd_fabric_event_details_v0`, `sd_pbsy_rcv_v0`, `sd_fcprdchkerr_v0`
- SCSI wrappers and payloads: `sd_scsi_event_details_v0`, `sd_scsi_generic_v0`, `sd_scsi_checkcond_v0`, `sd_scsi_varquedepth_v0`

Defines callback type `sd_callback` and registration APIs:

- `DFC_SD_RegisterForEvent`
- `DFC_SD_unRegisterForEvent`

## Integration Notes

This header references `HBA_WWN`, so it depends on HBA API types included earlier by consumers. It is explicitly intended for app/libdfc communication, not only kernel-internal use.

## Risks and Gotchas

- `struct sd_event` contains `size_t` and a raw `void *`, so it is not a stable cross-architecture serialized wire format without wrapping.
- Callback parameter name appears as `ort_id`, likely a typo for `port_id`; ABI is unaffected but generated docs or bindings may expose it.
- Event payload versions are embedded per structure, suggesting consumers should inspect version fields before decoding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_sdapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_thread.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_thread.h

## Purpose

Defines lightweight thread and task-queue state structures used by the `emlxs` driver.

## Main Definitions

- `EMLXS_MAX_TASKQ_THREADS` is `4`.
- `emlxs_thread_t`: doubly linked thread object with HBA pointer, kernel thread pointer, flags, function pointer, two arguments, mutex, and condition variable.
- `emlxs_taskq_thread_t`: singly linked taskq worker object with parent taskq pointer, kernel thread pointer, flags, function pointer, argument, mutex, and condition variable.
- `emlxs_taskq_t`: fixed array of taskq threads plus HBA pointer, get/put queues, counters, open flag, and separate get/put locks.
- Thread flags:
  - `EMLXS_THREAD_INITD`
  - `EMLXS_THREAD_STARTED`
  - `EMLXS_THREAD_ASLEEP`
  - `EMLXS_THREAD_BUSY`
  - `EMLXS_THREAD_KILLED`
  - `EMLXS_THREAD_ENDED`
  - `EMLXS_THREAD_TRIGGERED`
  - `EMLXS_THREAD_RUN_ONCE`

## Integration Notes

This header defines only data structures and flags. Thread lifecycle, queue operations, and synchronization semantics live in implementation files.

## Risks and Gotchas

- The task queue uses fixed storage for four worker slots; callers must not assume dynamic scaling.
- `emlxs_thread_t` has two argument pointers while taskq workers have one; callbacks must match the implementation’s dispatch convention.
- Separate get/put locks imply producer/consumer coordination outside this header; misuse can corrupt queue heads or counts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_thread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_version.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_version.h

## Purpose

Defines version, revision, copyright, and display-label strings for the `emlxs` driver and firmware.

## Main Definitions

- `EMLXS_COPYRIGHT`: Emulex copyright string.
- `EMLXS_VERSION`: `"2.80.9.0"`.
- Date components:
  - minute `50`
  - hour `16`
  - day `16`
  - month `01`
  - year `2024`
- `EMLXS_REVISION`: concatenates date components as `YYYY.MM.DD.HH.MM`.
- `EMLXS_NAME`: combines `DRIVER_NAME`, date, and version for FCA naming.
- `EMLXS_LABEL`: combines `VERSION`, `EMLXS_ARCH`, `MACH`, and `EMLXS_VERSION`.
- `EMLXS_FW_NAME`: combines `DRIVER_NAME`, date, and version for firmware naming.

## Integration Notes

This header expects macros such as `DRIVER_NAME`, `VERSION`, `EMLXS_ARCH`, and `MACH` to be defined by including context or build configuration.

## Risks and Gotchas

- The string concatenation relies on adjacent string literals and macro expansion. Missing build macros will cause compile failures.
- Version date and semantic version are independent constants; release tooling must update both consistently.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_version.h -->