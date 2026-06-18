# Research: subset-b-004404 Chelsio cxgb4 hardware contract headers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_hw.h

## Purpose

`t4_hw.h` is a compact hardware-constant contract for the Chelsio T4-family Ethernet driver. It centralizes adapter-wide dimensions, queue and mailbox sizes, SGE response descriptor layouts, flash partition offsets, PCIe memory window identifiers, and optical-module EEPROM/SFP diagnostic constants. The file does not implement behavior; it gives `cxgb4` C code stable symbolic names for hardware limits and wire/register bit encodings.

## Important APIs, Types, and Constants

- Global dimensions include `NCHAN`, `MAX_MTU`, `EEPROMSIZE`, `EEPROMVSIZE`, `EEPROMPFSIZE`, `RSS_NENTRIES`, `T6_RSS_NENTRIES`, `TCB_SIZE`, `NMTUS`, `NCCTRL_WIN`, `NTX_SCHED`, `PM_NSTATS`, `T6_PM_NSTATS`, `MBOX_LEN`, `TRACE_LEN`, and `FILTER_OPT_LEN`.
- Debug/logic-analyzer sizes include `CIM_NUM_IBQ`, `CIM_NUM_OBQ`, `CIM_NUM_OBQ_T5`, `CIMLA_SIZE`, `CIM_PIFLA_SIZE`, `CIM_MALA_SIZE`, `CIM_IBQ_SIZE`, `CIM_OBQ_SIZE`, `TPLA_SIZE`, and `ULPRX_LA_SIZE`.
- `enum ctxt_type` defines SGE context categories: `CTXT_EGRESS`, `CTXT_INGRESS`, `CTXT_FLM`, and `CTXT_CNM`.
- SGE constants describe work request size, context size, interrupt timer/counter counts, doorbell queue timer count, ingress queue max size, queue index granularity, interrupt destinations, ingress update delivery modes, host flow-control modes, fetch burst encodings, flush thresholds, and ingress padding shifts.
- `enum pcie_memwin` names PCIe BAR memory windows for NIC, RDMA, FCoE/iSCSI, and CSIO storage access.
- `struct sge_qstat` is a big-endian queue status entry containing `qid`, `cidx`, and `pidx`.
- `struct rsp_ctrl` describes the last 128 bits of an SGE response descriptor and exposes header-buffer length, payload-buffer length, QID, response type, generation bit, and final flit.
- Bit helpers include `RSPD_NEWBUF_*`, `RSPD_LEN_*`, `RSPD_QID_*`, `RSPD_TYPE_*`, `QINTR_CNT_EN_*`, `QINTR_TIMER_IDX_*`, and `SGE_TIMESTAMP_*`.
- Flash layout macros compute byte offsets and maximum sizes from sector numbers. Named sections cover expansion ROM, iBFT/driver parameters, boot configuration, firmware image, firmware bootstrap, iSCSI and FCoE crash/persistent areas, firmware configuration, FPGA configuration, minimum supported flash size, and failover-reserved sectors.
- Optical EEPROM/SFP constants include I2C device addresses `I2C_DEV_ADDR_A0` and `I2C_DEV_ADDR_A2`, `I2C_PAGE_SIZE`, SFP diagnostic type and SFF revision fields, and feature bits such as `SFP_DIAG_ADDRMODE` and `SFP_DIAG_IMPLEMENTED`.

## Control Flow and State Behavior

This header has no executable control flow. Its constants drive control flow elsewhere by bounding loops over channels, queues, timers, RSS tables, MTU tables, flash sectors, CIM buffers, and SGE contexts. The response descriptor helpers define how RX completion handlers interpret descriptor state, especially buffer ownership, response type, queue identity, and generation rollover. Flash layout constants determine persistent address ranges used by firmware-update, configuration, and crash-log routines.

Persistent state represented by this file is external hardware or nonvolatile media state. The header names flash regions but does not read, write, erase, validate, or persist anything itself. It also describes descriptor/status memory written by hardware and consumed by the driver, but it owns no in-memory state.

## Dependencies and Integration Points

- Includes `<linux/types.h>` for fixed-width and endian-qualified kernel types.
- Uses `BIT()` for SFP diagnostic feature bits; callers must include a Linux bitops context that provides it.
- Integrates with SGE queue setup and completion paths through `struct sge_qstat`, `struct rsp_ctrl`, SGE mode constants, and interrupt deferral fields.
- Integrates with firmware, flash, and EEPROM code through flash offsets, sizes, and I2C/SFP field addresses.
- Integrates with PCIe memory access code through `enum pcie_memwin`.
- Closely complements `t4_regs.h`, `t4_msg.h`, `t4_tcb.h`, and `t4_values.h`: this file gives high-level dimensions while those headers provide register, CPL message, TCB, and register-value details.

## Risks and Edge Cases

- The constants are hardware ABI. Incorrect values silently corrupt queue sizing, descriptor parsing, flash offsets, or firmware mailbox access.
- T4/T5/T6 differences are embedded in separate constants such as `T6_RSS_NENTRIES`, `T6_PM_NSTATS`, and `CIM_NUM_OBQ_T5`; call sites must select by adapter generation.
- `struct rsp_ctrl` relies on big-endian fields and packed hardware layout expectations. Consumers must continue using endian conversions and avoid assuming host endianness.
- Flash region sizes and `FLASH_MIN_SIZE` encode assumptions about sector size and fixed layout; firmware update code must not use them for incompatible flash parts without explicit generation checks.
- The file defines broad constants in the global macro namespace, so new names can collide with nearby hardware headers if not kept specific.

## Test Signals

- Build coverage of `cxgb4` catches missing type/macro dependencies and field-name regressions.
- Queue bring-up and RX/TX traffic tests validate SGE dimensions, response descriptor parsing, and interrupt deferral values.
- Firmware update/configuration tests validate flash region offsets and minimum-size checks.
- EEPROM/SFP diagnostics via ethtool or driver debug paths validate I2C offsets and feature bits.
- Adapter matrix testing across T4, T5, and T6 is important because this header contains generation-specific table sizes and stats counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_msg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_msg.h

## Purpose

`t4_msg.h` defines the Chelsio Protocol Layer (CPL), work request, RSS, ULP, tunnel LSO, TLS/security, iSCSI, RDMA, L2T, SMT, and firmware wrapper message formats consumed and produced by the `cxgb4` driver. It is a hardware/firmware ABI header: structures map to big-endian descriptor payloads and macros pack or extract bitfields for commands placed on SGE queues or received from hardware/firmware.

## Important APIs, Types, and Constants

- CPL opcode enum covers connection management (`CPL_PASS_OPEN_REQ`, `CPL_ACT_OPEN_REQ`, `CPL_PASS_ACCEPT_REQ`, establish/close/abort/release), data path (`CPL_TX_DATA`, `CPL_RX_DATA`, `CPL_TX_PKT`, `CPL_RX_PKT`), offloads (`CPL_ISCSI_*`, `CPL_RDMA_*`, `CPL_TX_TLS_*`, `CPL_TLS_DATA`, `CPL_RX_TLS_CMP`), firmware wrappers (`CPL_FW4_MSG`, `CPL_FW6_MSG`, payload/ack forms), table operations (`CPL_L2T_WRITE_REQ`, `CPL_SMT_WRITE_REQ`, `CPL_SRQ_TABLE_REQ`), and tunnel/LSO commands (`CPL_TX_TNL_LSO`, `CPL_TX_PKT_LSO`, `CPL_TX_PKT_XT`).
- `enum CPL_error` defines firmware/hardware status values such as TCAM miss/full, bad length/route/SYN, connection reset/existing/timed-out, ARP miss, retransmit/persist/keepalive advice, abort failure, and iWARP/embedded reply indicators.
- Mode enums define connection policy, ULP modes (`NONE`, `ISCSI`, `RDMA`, `TCPDDP`, `FCOE`, `TLS`), CRC flags, abort reset behavior, TX checksum types, congestion algorithms, firmware wrapper types, ULP TX opcodes, ULP TX scatter/gather subcommands, and tunnel LSO types.
- `union opcode_tid` and helpers `CPL_OPCODE_*`, `TID_G`, `MK_OPCODE_TID`, `OPCODE_TID`, `GET_TID`, `TID_TID_*`, and `TID_QID_*` encode/decode the common opcode/TID word.
- `struct rss_header` carries RX opcode, channel/filter/hash metadata, queue id, and hash value with endian-dependent bitfield layout.
- `struct work_request_hdr` plus `WR_HDR` are embedded in outbound work requests. `WR_OP_V()` and related option-field macros pack WR operation and connection options.
- Connection-management structures include passive-open requests/replies, IPv6 variants, accept requests/replies including T5 reply form, active-open T4/T5/T6 IPv4/IPv6 requests, open replies, establish notifications, TCB get/set requests/replies, close server/connection requests/replies, abort request/reply RSS and WR forms, peer close, and TID release.
- TX/RX packet structures include `cpl_tx_pkt_core`, `cpl_tx_pkt`, `cpl_tx_pkt_lso_core`, `cpl_tx_pkt_lso`, `cpl_tx_data`, `cpl_rx_data`, `cpl_rx_data_ack`, and `cpl_rx_pkt`. Macros pack checksum, VLAN, timestamp, LSO, header length, tunnel, and RX error vector fields.
- iSCSI/DDP structures include `cpl_iscsi_hdr`, `cpl_rx_data_ddp`, `cpl_iscsi_data`, `cpl_rx_iscsi_cmp`, and `cpl_tx_data_iso`.
- L2/SMT structures include `cpl_l2t_write_req/rpl`, `cpl_smt_write_req/rpl`, and `cpl_t6_smt_write_req`.
- Firmware wrappers include `cpl_fw4_pld`, `cpl_fw6_pld`, `cpl_fw4_msg`, `cpl_fw4_ack`, `cpl_fw6_msg`, and `cpl_fw6_msg_ofld_connection_wr_rpl`.
- ULP and memory I/O structures include `ulptx_sge_pair`, `ulptx_sgl`, `ulptx_idata`, `ulp_txpkt`, `ulp_mem_io`, and `ulptx_sc_memrd`.
- Tunnel and security structures include `cpl_tx_tnl_lso`, `cpl_tx_sec_pdu`, `cpl_tx_tls_sfo`, `cpl_tls_data`, and `cpl_rx_tls_cmp`.
- Other receive/control messages include trace packets, RDMA terminate, SGE egress update, RX physical DSGL, RX MPS packet, and SRQ table request/reply.

## Control Flow and State Behavior

The header has no functions or executable branches. It shapes driver control flow by letting call sites construct outbound CPL work requests and dispatch inbound completions by opcode. Typical flows are:

- Passive listen setup sends a passive-open request, receives accept requests, replies with accept parameters, and later receives establish/close/abort messages.
- Active open sends an active-open request with generation-specific T4/T5/T6 layout and handles open-reply or establish messages.
- TCB operations send get/set messages using `TCB_WORD`, cookie, mask, and value fields and correlate replies by cookie/status.
- TX packet paths build `cpl_tx_pkt`, `cpl_tx_pkt_lso`, `cpl_tx_tnl_lso`, or `cpl_tx_data` structures before pushing descriptors to SGE queues.
- RX paths decode `rss_header`, `cpl_rx_pkt`, `cpl_rx_data`, TLS/iSCSI completion messages, and hardware error/status fields.
- Firmware events are wrapped in CPL FW4/FW6 messages and then dispatched by nested firmware type.

The state represented here is transport/offload state held by firmware and ASIC tables: TIDs, STIDs/ATIDs, TCB words, L2 table entries, SMT entries, SRQ state, TLS key/context state, RSS queue routing, and sequence/window values. The header owns none of that state; it only defines the serialized representation and bitfield accessors.

## Dependencies and Integration Points

- Includes `<linux/types.h>` for fixed-width, `__be*`, and `__u*` kernel types.
- Macros such as `GET_TID()` depend on `be32_to_cpu()` being visible in including translation units.
- Endian-dependent bitfields depend on Linux `__LITTLE_ENDIAN_BITFIELD` conventions.
- Integrates directly with SGE TX/RX queue code, offload connection manager code, TOE/iSCSI/RDMA/TLS paths, L2 table and source MAC table management, firmware mailbox/event handling, and RSS receive dispatch.
- Uses TCB word definitions from `t4_tcb.h` at call sites, register constants from `t4_regs.h`, and modal values from `t4_values.h`.
- T4/T5/T6 compatibility is represented by parallel structure variants and generation-specific field macros, so adapter-version selection must happen at the call sites.

## Risks and Edge Cases

- This is wire-format ABI. Structure padding, field order, endian conversion, or bit shifts cannot change without breaking hardware/firmware communication.
- Several fields are generation-specific: T5/T6 active-open request layout, T6 header-length fields, T5/T6 TX/RX header encodings, T6 SMT write form, and T6 TX force bit. Using the wrong form for an adapter can produce failed opens, malformed packets, or firmware errors.
- Bitfield layout in `rss_header`, `tcp_options`, `cpl_rx_data`, and trace messages is controlled by endian preprocessor macros; unsupported endian configurations need careful build validation.
- Many macros only shift values and do not mask on write. Callers must pass bounded field values or risk overwriting neighboring bits.
- Some macro names are repeated or aliased, for example `ULPTX_CMD_S`, `ULP_TX_SC_MORE_*`, and `RXF_SYN_*`. Reuse reflects hardware manuals but increases collision/confusion risk.
- The `ULP_TXPKT_DATAMODIFY_G()` macro references `ULP_TXPKT_DATAMODIFY__M` with a double underscore, which appears inconsistent with the defined `ULP_TXPKT_DATAMODIFY_M`; this should be build-covered if the getter is used.
- Flexible array `struct ulptx_sgl::sge[]` requires correct allocation/descriptor length calculation by callers.
- Security/TLS and tunnel LSO fields have many interdependent offsets/lengths. Incorrect payload lengths or header offsets can create malformed packets or crypto offload failures.

## Test Signals

- Compile `cxgb4` with all enabled offload paths to catch structure, macro, and endian dependency regressions.
- Active/passive TCP offload connection tests should cover open, establish, close, abort, TID release, TCB get/set, and error replies.
- RX/TX traffic tests should cover plain packets, checksum offload, VLAN, timestamping, LSO, tunnel LSO, and compressed RX error fields.
- iSCSI, RDMA, and TLS offload tests validate the specialized CPL structures and length/offset packing.
- Firmware command/event tests validate FW4/FW6 wrapper decoding and `cpl_fw4_ack` flag handling.
- Sparse/compiler warnings and structure-size assertions, if present in surrounding code, are valuable because this file is mostly layout definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_pci_id_tbl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_pci_id_tbl.h

## Purpose

`t4_pci_id_tbl.h` is an include-time PCI device ID table generator for Chelsio T4, T5, and T6 adapters. It keeps the adapter product ID list in one header while letting different users define macros that expand each entry into the desired table type, function number, and table wrapper.

## Important APIs, Types, and Constants

- Required includer macros:
  - `CH_PCI_DEVICE_ID_TABLE_DEFINE_BEGIN` starts the generated table.
  - `CH_PCI_DEVICE_ID_FUNCTION` selects the PCI function nibble inserted into each ID.
  - `CH_PCI_ID_TABLE_ENTRY(DeviceID)` emits one table entry.
  - `CH_PCI_DEVICE_ID_TABLE_DEFINE_END` finishes the table and supplies the semicolon.
- Optional `CH_PCI_DEVICE_ID_FUNCTION2` makes every product ID emit two entries, one for each function value.
- `CH_PCI_ID_TABLE_FENTRY(devid)` combines the base product ID with the selected function nibble using `((CH_PCI_DEVICE_ID_FUNCTION) << 8)`.
- The header enumerates many T4 IDs (`0x4000` series), T5 IDs (`0x5000` and custom `0x5080`+ series), and T6 IDs (`0x6001` etc. and custom `0x6080`+ series).
- The device ID scheme is documented as `0xVFPP`: ASIC generation in `V`, function in `F`, and product designation in `PP`.

## Control Flow and State Behavior

The file has no runtime control flow. It uses preprocessor control flow to reject missing required macros, define the per-function expansion macro differently depending on whether `CH_PCI_DEVICE_ID_FUNCTION2` is present, and emit the table in manifest order. It owns no state and performs no persistence; its output becomes static driver data in the translation unit that includes it.

## Dependencies and Integration Points

- Intended to be included by PCI driver code that defines Linux PCI ID table wrappers around it, likely using `PCI_DEVICE()`-style entries and `MODULE_DEVICE_TABLE()`.
- Integrates with probe binding: IDs emitted here determine which Chelsio adapters bind to a given driver or function role.
- Shares generation/product naming with the rest of the `cxgb4` adapter initialization logic, which later maps detected device IDs to chip version and port capabilities.
- The include contract deliberately avoids direct Linux PCI header dependency by requiring the includer to supply the table-entry macro.

## Risks and Edge Cases

- Because the header requires caller-provided macros, a malformed includer can generate syntactically valid but semantically wrong tables.
- Missing a product ID prevents automatic driver binding for that adapter; adding an incorrect ID can bind unsupported hardware.
- `CH_PCI_DEVICE_ID_FUNCTION` and optional function 2 must match the driver role: PF0-3, PF4, VF, or other function spaces. Wrong values generate IDs for the wrong PCI function class.
- The file uses a trailing comma strategy inside `CH_PCI_ID_TABLE_FENTRY()` and relies on `CH_PCI_DEVICE_ID_TABLE_DEFINE_END` to close with a semicolon; unusual table macros must tolerate that style.
- T6 entries are less richly commented than T4/T5, so product mapping may require cross-checking with vendor release notes or adjacent driver tables before edits.

## Test Signals

- Build tests catch missing macro definitions, bad table syntax, and duplicate macro expansion issues.
- `modinfo`/module alias output can confirm expected PCI aliases for generated IDs.
- Probe tests on representative T4/T5/T6 PFs and VFs confirm function-nibble correctness.
- PCI ID diff review is important whenever hardware support is added, because runtime tests only cover physically present adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_pci_id_tbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_regs.h

## Purpose

`t4_regs.h` defines the memory-mapped register address map and bitfield helpers for Chelsio T4/T5/T6 adapters. It is the driver’s primary register ABI reference, covering PF/port address helpers, SGE queues and interrupts, PCIe, memory controllers, CIM/mailboxes, TP offload engine, PM/ULP datapaths, MPS/MAC statistics and tracing, RSS/filter/LE database control, serial flash, PL top-level interrupts, NCSI/SMB, and T5/T6-specific register deltas.

## Important APIs, Types, and Constants

- Address helpers: `MYPF_REG`, `PF_REG`, `MYPORT_REG`, `PORT_REG`, `EDC_REG`, `PCIE_MEM_ACCESS_REG`, `PCIE_MAILBOX_REG`, `MC_BIST_STATUS_REG`, `EDC_BIST_STATUS_REG`, `PCIE_FW_REG`, `T5_PORT_REG`, `MC_REG`, and `EDC_T5_REG`.
- SGE block: PF/VF doorbells, GTS, control registers, context command/data, host page size, queues-per-page, interrupt cause/enable registers, free-list buffers, ingress thresholds, congestion-manager control, timestamp, DBFIFO/DBVFIFO status, doorbell control, timer values, debug data, error stats, and DBQ context base. Bitfields cover QID/PIDX/CIDX, boundaries, VFIFO, context type/QID, per-PF page sizes, queue errors, dropped doorbells, HP/LP FIFO thresholds/counts, stat modes, and T5/T6 differences.
- PCIe block: PF config/CLI/expansion ROM offset, interrupt cause and nonfatal error fields, configuration-space access registers, memory access base/offset windows, firmware registers, core status registers, and static spare configuration version.
- Memory blocks: MC/MC_P ECC status, interrupt cause, BIST command/address/length/pattern/status; MA EDRAM/external-memory BARs, target memory enable, wrap/parity status; EDC base/stride, BIST, ECC and parity status.
- CIM block: boot/SDRAM/extmem configuration, PF mailbox data/control/shadow, mailbox ownership/valid/interrupt bits, host interrupt cause/enable, host upper-access errors, host access control/data, IBQ/OBQ debug configuration/data, queue configuration, logic analyzer/debug pointers, and queue address/counter fields.
- TP block: debug logic analyzer, global/output config, CMM/PMM base and max-page registers, timer resolution, retransmit/persist/keepalive/delayed-ack timers, shift counts, congestion-control/pace/MTU/RSS lookup tables, PIO/MIB access, FLM free counts, offload/tunnel rates, VLAN priority map/filter tuple selection, ingress checksum/VNIC config, RSS config/key/VF/PF maps, and TX scheduler/modulation registers.
- ULP/PM blocks: ULP TX interrupt and table limit registers, TX logic analyzer/debug registers, PM RX/TX interrupt/stat/debug registers, framing and parity error bits, ULP RX limits for iSCSI/TDDP/STAG/RQ/PBL/TLS key memory, and ULP RX logic analyzer registers.
- MPS/MAC blocks: per-port TX/RX/loopback statistics, magic MAC and PTP timestamp/sum registers, MAC/XGMAC EPIO access, common/stat/interrupt controls, TX/RX FIFO parity, background drop/truncate stats, trace configuration/RSS/filter controls, classifier TCAM/SRAM data/control, VF replication maps, VXLAN/GENEVE UDP type configuration, and T5/T6 MPS classifier sizing.
- LE/CPL/PL/SF/NCSI/SMB blocks: CPL interrupt cause, SMB/NCSI parity interrupts, serial flash data/op and busy/lock/cont/byte/op bits, PF/top-level PL interrupts/enables/reset/revision/whoami, LE database config/hash/table/index/count/interrupt/response code registers, and T6 LE hash mask registers.

## Control Flow and State Behavior

This header has no executable control flow. It drives control flow in hardware access routines that compute register addresses, poll busy bits, read interrupt causes, write enables, configure queues, and decode status registers. Common usage patterns implied by the constants include:

- Queue setup writes SGE control, page-size, free-list buffer, context, and doorbell registers, then uses GTS/doorbell fields for runtime producer/consumer updates.
- Interrupt handlers read module-level and top-level cause registers, mask individual bits, clear handled causes, and may query error status registers for queue IDs or ECC counts.
- Firmware/mailbox code uses CIM PF mailbox data/control registers and mailbox owner/valid/interrupt fields to arbitrate between driver and firmware.
- Memory diagnostics use MC/EDC BIST command/status and ECC/parity counters.
- RSS/filter/offload configuration writes TP RSS, VLAN priority map, LE database, and MPS classifier registers.
- Debug and ethtool paths use logic analyzer, MIB/stat, trace, TCAM/SRAM, and queue debug registers.

The persistent state is entirely in hardware registers, adapter memory, EEPROM/flash-related access paths, or firmware-owned tables. The header names locations and bit meanings but does not itself persist state. Register writes made by callers may survive until reset, firmware reload, or explicit reconfiguration, depending on the hardware block.

## Dependencies and Integration Points

- No explicit includes; it is pure preprocessor definitions.
- Integrated by low-level adapter code that performs MMIO register reads/writes, interrupt setup, firmware communication, diagnostics, statistics collection, RSS/filter setup, and hardware bring-up/reset.
- Complements `t4_values.h`, which supplies modal values for some fields defined here, and `t4_hw.h`, which supplies global dimensions used to iterate register instances.
- Works with `t4_msg.h` and `t4_tcb.h` indirectly: register programming enables queues and offload engines that exchange CPL messages and manipulate TCB state.
- Address helpers encode PF/port/generation layout assumptions, so they are central integration points for SR-IOV, PF-specific mailbox, port-stat, and T5/T6 access paths.

## Risks and Edge Cases

- Register offsets and bit positions are strict hardware ABI. A wrong value can disable queues, break interrupts, corrupt adapter memory, or misdiagnose fatal errors.
- Many `_V(x)` macros do not mask input before shifting. Callers must validate field widths using the corresponding `_M` values where provided.
- Some names are deliberately repeated for registers/bits reused in multiple contexts, such as `SGE_DOORBELL_CONTROL_A`, `SGE_CTXT_CMD_A`, `ENABLE_DROP_*`, `HP_INT_THRESH_*`, and `DATALKPTYPE_*`. This is legal in C only when definitions match; future edits must avoid incompatible redefinitions.
- T5/T6 variants have different shifts, widths, base addresses, port strides, classifier sizes, and source-PF encodings. Incorrect generation checks in callers are high risk.
- Several registers are indexed or strided; callers must bound indices against instance-count constants such as `NUM_LE_DB_DBGI_REQ_DATA_INSTANCES`, `NUM_MPS_CLS_TCAM_Y_L_INSTANCES`, `NUM_MPS_CLS_SRAM_L_INSTANCES`, and T5/T6 variants.
- Busy bits such as SGE context busy, LE DB debug busy, SF busy, CIM host busy, and IBQ/OBQ debug busy require timeout handling in callers to avoid hangs on faulty hardware.
- Top-level interrupt bits aggregate submodule failures; handlers must read the subordinate cause registers before clearing or masking to avoid losing diagnostic information.

## Test Signals

- Full driver build catches duplicate macro mismatches and missing definitions.
- Adapter bring-up on T4/T5/T6 validates PF/port base helpers, SGE setup, mailbox ownership, and PL interrupt routing.
- TX/RX traffic with interrupts and NAPI validates doorbell/GTS, queue status, SGE timers, and error paths.
- ethtool statistics and diagnostics validate MPS/MAC/TP MIB offsets, PM/ULP counters, and debug register reads.
- Firmware flash/mailbox operations validate CIM mailbox and serial flash register sequences.
- Fault-injection or hardware error tests should verify ECC/parity/interrupt bits and queue error reporting.
- RSS/filter/tunnel tests validate TP RSS, LE DB, MPS classifier, VXLAN, and GENEVE register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_tcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_tcb.h

## Purpose

`t4_tcb.h` defines bit positions, word indices, masks, and value macros for fields in the Chelsio TCP Control Block (TCB). The TCB is firmware/ASIC connection state for TOE/offload connections. This header lets driver code build CPL TCB get/set commands and interpret or modify specific connection fields without hard-coding word offsets.

## Important APIs, Types, and Constants

- TCB word/field macros follow the pattern `TCB_<FIELD>_W`, `_S`, `_M`, and `_V(x)` for word index, shift, mask, and encoded value.
- Link/source fields include `TCB_L2T_IX`, `TCB_SMAC_SEL`, and `TCB_RSS_INFO`.
- `TCB_T_FLAGS` covers a full 64-bit TCB flag word; `TCB_FIELD_COOKIE_TFLAG` identifies a cookie value associated with T-flags operations.
- TCP state and timing fields include `TCB_T_STATE`, `TCB_TIMESTAMP`, `TCB_RTT_TS_RECENT_AGE`, and `TCB_T_RTSEQ_RECENT`.
- Sequence/window fields include `TCB_TX_MAX`, `TCB_SND_UNA_RAW`, `TCB_SND_NXT_RAW`, `TCB_SND_MAX_RAW`, `TCB_RCV_NXT`, and `TCB_RCV_WND`.
- RX/PDU and buffer fields include raw fragment word constants, `TCB_PDU_HDR_LEN_W`, `TCB_RQ_START`, and `TF_RX_PDU_OUT`.
- T-flag bit shifts include `TF_DROP_S`, `TF_DIRECT_STEER_S`, `TF_LPBK_S`, `TF_CCTRL_ECE_S`, `TF_CCTRL_CWR_S`, `TF_CCTRL_RFR_S`, `TF_CORE_BYPASS_S`, and `TF_NON_OFFLOAD_S`.
- Flag helper macros provide `_V(x)` and `_F` forms for boolean flags such as `TF_CORE_BYPASS_F` and `TF_NON_OFFLOAD_F`.

## Control Flow and State Behavior

The file has no executable control flow. It participates in runtime flows when the driver sends `CPL_GET_TCB`, `CPL_SET_TCB_FIELD`, or core TCB-field messages defined in `t4_msg.h`. A caller chooses the TCB word, mask, and value from this header, sends the CPL command to firmware/hardware, and later handles the reply or observes changed connection behavior.

The state addressed by these macros is persistent connection state inside the adapter TCB memory for the life of an offloaded connection. This header does not store state locally, but its constants determine which hardware state is read or mutated.

## Dependencies and Integration Points

- Uses `__u64` in several macros but does not include a type header itself; includers must already have Linux types available.
- Integrates tightly with `t4_msg.h` TCB commands, especially `struct cpl_get_tcb`, `struct cpl_set_tcb_field`, `TCB_WORD_V()`, and cookie/status handling.
- Used by connection management, filter/direct-steering, loopback, congestion-control, non-offload/core-bypass, DDP/PDU, and diagnostics code that needs to inspect or alter adapter connection state.
- Complements `t4_hw.h` `TCB_SIZE` and `t4_regs.h` TP/LE/offload register definitions.

## Risks and Edge Cases

- TCB word/shift/mask values are ABI-sensitive. A wrong offset can modify the wrong connection state and create hard-to-debug traffic corruption or connection teardown.
- The header contains a duplicate definition block for `TCB_T_FLAGS_*`; it is identical, but future edits must keep duplicate definitions synchronized or remove duplication carefully.
- Several `_V(x)` macros do not cast to `__u64`, while fields are 64-bit; callers passing narrow or signed values should ensure correct width before shifting.
- No `_G(x)` getters are provided for most fields; decode paths need to apply shifts/masks manually or add helpers consistently.
- Generation-specific TCB layout differences, if any are introduced elsewhere, must be reflected here with explicit new macros rather than overloading existing names.

## Test Signals

- Compile coverage of all TCB operations catches missing type dependencies and macro spelling issues.
- TOE/offload connection tests validating direct steering, drop, loopback, non-offload, congestion-control, window, and sequence behavior provide functional coverage.
- TCB dump/debug tests can compare decoded fields against firmware/hardware expectations.
- Negative tests should verify that invalid masks/words are rejected by firmware or handled cleanly by the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_tcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_values.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_values.h

## Purpose

`t4_values.h` defines named hardware values for modal register fields in the Chelsio T4-family driver. Unlike `t4_regs.h`, which mostly defines register addresses and bit positions, this file names the concrete encoded values that callers write into those fields, especially for SGE behavior, congestion-manager modes, BAR2 user doorbell layout, mailbox owners, PCIe window shifts, and filter tuple composition.

## Important APIs, Types, and Constants

- SGE `CONTROL1`/`CONTROL2` values define RX packet CPL split mode, ingress PCIe/padding/packing boundary shifts and encodings, T6-specific padding encodings, GTS timer/counter registers, fetch burst min/max encodings, host flow-control modes, CIDX flush thresholds, update delivery mode, and response descriptor type values.
- Congestion manager helpers define context bit positions and values for channel- or queue-based congestion modes: `CONMCTXT_CNGTPMODE_*`, `CONMCTXT_CNGCHMAP_*`, `CONMCTXT_CNGTPMODE_CHANNEL_X`, and `CONMCTXT_CNGTPMODE_QUEUE_X`.
- BAR2/user doorbell layout constants define `SGE_UDB_SIZE`, kernel/simple doorbell offset `SGE_UDB_KDOORBELL`, GTS offset `SGE_UDB_GTS`, and write-combining doorbell offset `SGE_UDB_WCDOORBELL`.
- CIM mailbox owner constants include `X_MBOWNER_FW` and `X_MBOWNER_PL`.
- PCIe helper shifts define `WINDOW_SHIFT_X` and `PCIEOFST_SHIFT_X`.
- Compressed filter tuple widths define optional fields for FCoE, port, VNIC ID, VLAN, TOS, protocol, EtherType, MAC match, MPS hit type, and fragmentation.
- Filter tuple subfield helpers define VLAN-valid, VNID VF/PF ID, and VNID valid fields.

## Control Flow and State Behavior

This header has no executable control flow. It is used by initialization and configuration paths that choose encoded register values before writing registers from `t4_regs.h`. For example, SGE initialization selects ingress padding/packing boundaries, fetch burst sizes, host flow-control behavior, response types, and interrupt delivery modes. BAR2 doorbell setup uses the user-doorbell offsets to choose between simple doorbells, GTS writes, and write-combining doorbell buffers.

The state affected by these values lives in adapter registers, queue contexts, and filter configuration registers. The header owns no local state and performs no persistence.

## Dependencies and Integration Points

- Pure macro header with no includes.
- Integrates directly with `t4_regs.h` register fields such as SGE control, GTS, host flow-control, doorbell, PCIe window, CIM mailbox owner, TP VLAN priority map, and filter tuple configuration.
- Complements `t4_hw.h` SGE mode constants and `t4_msg.h` response/CPL type definitions.
- Used by filter-building code to calculate compressed filter tuple widths and set validity/subfield bits.

## Risks and Edge Cases

- These constants are encoded hardware values, not arbitrary software enums. Confusing `_X` encoded values with shifts or raw byte counts can program the wrong mode.
- T6 changes several SGE encodings (`T6_INGPADBOUNDARY_*`, `FETCHBURSTMIN_*_T6_X`); callers must choose values based on chip generation.
- BAR2 doorbell offsets are chosen to avoid undesirable write combining. Moving them or using the wrong offset can affect queue notification correctness and performance.
- Filter tuple width constants must stay synchronized with `TP_VLAN_PRI_MAP` semantics and tuple-building code; mismatches can shift later fields and break filter matching.
- `_V(x)` helpers here generally do not mask inputs, so callers must only pass bounded values.

## Test Signals

- Build coverage verifies macro availability and spelling.
- Queue initialization and high-rate TX/RX tests validate SGE modal values, burst settings, doorbell offsets, and response type expectations.
- T5/T6 adapter tests validate generation-specific padding and fetch-burst choices.
- Filter insertion/match tests validate compressed tuple widths and VLAN/VNIC subfield packing.
- Firmware mailbox tests validate owner values used with CIM mailbox control fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_values.h -->
