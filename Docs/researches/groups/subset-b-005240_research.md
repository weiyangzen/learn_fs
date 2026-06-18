# Research Report: subset-b-005240

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa.h

## Purpose
`bfa.h` is the central HAL-facing public header for the QLogic/Brocade BR-series Fibre Channel adapter layer. It connects the driver-facing `bfad` code, common-service helpers, BFI firmware messaging, IOC management, and service definitions into one control plane for queue management, interrupts, IOCFC lifecycle, completion callbacks, and adapter query helpers.

## Important APIs, Types, and Macros
The key type is `struct bfa_iocfc_s`, which owns the IOCFC state machine pointer, firmware/driver configuration, request/response circular queue indices, queue DMA descriptors, shadow producer/consumer DMA areas, firmware configuration request/response pages, device register pointers, chip-specific `struct bfa_hwif_s`, callback queue entries, Fabric Assigned Address query state, and IOCFC memory descriptors. Queue macros such as `bfa_reqq_next`, `bfa_reqq_produce`, `bfa_reqq_full`, `bfa_rspq_pi`, `bfa_rspq_ci`, and `bfa_rspq_elem` define the ABI between host ring state and firmware queue registers. Callback helpers `bfa_cb_queue`, `bfa_cb_queue_once`, `bfa_cb_queue_status`, and pending queue initializers standardize deferred callback dispatch. Public lifecycle APIs include `bfa_cfg_get_default`, `bfa_cfg_get_meminfo`, `bfa_attach`, `bfa_detach`, `bfa_iocfc_init`, `bfa_iocfc_start`, `bfa_iocfc_stop`, `bfa_iocfc_enable`, `bfa_iocfc_disable`, and interrupt APIs `bfa_intx`, `bfa_isr_enable`, `bfa_isr_disable`, `bfa_msix_*`.

## Control Flow and State
This header declares the IOCFC event enum used by `bfa_core.c`: init/start/stop/enable/disable requests, IOC enabled/disabled/failure callbacks, dynamic configuration completion, and firmware config completion. The queue macros are control-flow critical because most modules reserve a firmware message with `bfa_reqq_next`, fill it, then publish it with `bfa_reqq_produce`, which stamps the hardware queue id and writes the new producer index to the mapped register.

## State and Persistence Behavior
State is in memory and hardware-facing DMA, not filesystem persistence. Persistent adapter settings enter via firmware/config flash responses and are exposed through `cfgrsp`, LUN mask accessors, boot WWN helpers, and adapter/IOC macros. Ring indices and shadow pointers are volatile coordination state shared with firmware and must preserve power-of-two queue sizing assumptions.

## Dependencies and Integration Points
It depends on `bfad_drv.h` for Linux driver primitives, `bfa_cs.h` for tracing/state-machine/list helpers, `bfa_defs_svc.h` for IOCFC service structs, `bfi.h` for firmware message layouts, and `bfa_ioc.h` for IOC services. Hardware callback declarations split CB, CT, and CT2 ASIC behavior behind `bfa_hwif_s`.

## Risks and Test Signals
High-risk areas are ring wrap math, DMA pointer alignment, endian conversion, callback queue lifetime, and missing hardware callback installation. Test signals include queue full/resume behavior under load, MSI-X and INTx interrupt paths, IOC init/disable/re-enable cycles, failed firmware config replies, min-config LUN mask returns, and all ASIC id branches for CB, CT, and CT2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_core.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_core.c

## Purpose
`bfa_core.c` implements the BFA HAL core for Fibre Channel adapters. It wires firmware interrupt dispatch tables, common tracing, IOCFC lifecycle state machines, DMA memory claiming, interrupt processing, firmware configuration handshakes, Fabric Assigned Address query handling, attach/detach, completion callback processing, and default resource configuration.

## Important APIs and Functions
The file defines ISR dispatch arrays `bfa_isrs` for BFI message classes and `bfa_mbox_isrs` for mailbox classes. Public entry points include `bfa_iocfc_meminfo`, `bfa_iocfc_attach`, `bfa_iocfc_init`, `bfa_iocfc_start`, `bfa_iocfc_stop`, `bfa_iocfc_isr`, `bfa_iocfc_get_attr`, `bfa_iocfc_israttr_set`, `bfa_iocfc_set_snsbase`, `bfa_iocfc_enable`, `bfa_iocfc_disable`, `bfa_iocfc_is_operational`, `bfa_iocfc_get_bootwwns`, `bfa_iocfc_get_pbc_vports`, `bfa_cfg_get_meminfo`, `bfa_attach`, `bfa_detach`, `bfa_comp_deq`, `bfa_comp_process`, `bfa_comp_free`, and `bfa_cfg_get_default`. Internal helpers attach common modules, initialize chip-specific hardware callbacks, claim DMA memory, configure queue registers, process firmware config responses, and start or disable submodules.

## Control Flow and State
The IOCFC FSM moves from `stopped` to `initing`, reads dynamic config, sends firmware config, queues the init callback, then waits for `START` to become `operational`. Operational entry initializes the FC port, starts submodules, enables queue processing, acknowledges response queues, and refreshes LUN mask runtime state. Stop paths write dynamic config, disable IOC, disable ISR handling, quiesce submodules, and queue completion. Enable/disable paths reuse IOC callbacks and optionally queue driver completions. Failure paths disable interrupts and submodules, then either wait for recovery or callback with failure.

## Interrupt and Queue Behavior
`bfa_intx` and `bfa_msix_all` read interrupt status, acknowledge queue causes, drain response queues with `bfa_isr_rspq`, resume request waiters with `bfa_reqq_resume`, and route error/mailbox interrupts through `bfa_msix_lpu_err`. Response queue messages are dispatched by message class, with unknown classes warning and stopping trace capture.

## State and Persistence Behavior
Persistent and firmware-derived state enters through the config response page. `bfa_iocfc_cfgrsp` converts firmware resource counts from big endian, installs queue register offsets, reconfigures resources, installs MSI-X queue handlers, and completes config only after PBC WWNs or FAA address messages are available. Boot WWNs and PBC vports are read from `cfgrsp`; no disk persistence is performed.

## Dependencies and Integration Points
The file integrates almost every BFA submodule: port, FCXP, LPS, UF, rport, FCP, task management, diagnostics, SFP, flash, PHY, FRU, CEE, adapter block, dynamic config, IOC, mailbox, and PCI register code. Firmware contracts come through `bfi_iocfc_*` messages and register offsets.

## Risks and Test Signals
Risk centers on asynchronous FSM events racing stop/disable/failure, queue processing during interrupt disable, firmware config endian handling, callback queue lifetime, and assuming power-of-two queue sizes. Test with init/start/stop, IOC failure during each FSM state, MSI-X and INTx interrupts, firmware config with reduced resources, FAA supported/unsupported paths, boot PBC extraction, and request queue exhaustion/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_cs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_cs.h

## Purpose
`bfa_cs.h` provides common services shared by the BFA driver: trace buffering, queue macros, state machine macros, wait counters, WWN/FCID formatting, and 24-bit Fibre Channel id endian conversion. It is infrastructure used by both HAL code and Fibre Channel control state machines.

## Important APIs and Types
`struct bfa_trc_mod_s` owns a circular trace buffer of `struct bfa_trc_s` entries, with head/tail counters, stop flag, and timestamps. `BFA_TRC_FILE`, `bfa_trc`, and `bfa_trc32` stamp a module/file id and source line into `__bfa_trc`. Queue helpers wrap Linux `list_head`: `bfa_q_deq`, `bfa_q_deq_tail`, `bfa_q_is_on_q`, and accessors for first/next/prev. `bfa_sm_*` macros provide simple state machines; `bfa_fsm_*` macros add entry actions. `struct bfa_wc_s` implements a small wait counter with a resume callback.

## Control Flow and State
State machine macros store a function pointer directly in the object being controlled. `bfa_fsm_set_state` updates the function pointer and immediately calls the new state entry function, which is why state transitions in `bfa_core.c` can perform side effects such as IOC enable, mailbox configuration, or callback queueing as soon as the transition occurs. The wait counter starts with a held reference; callers call `bfa_wc_wait` to drop it and run the resume callback when the count reaches zero.

## State and Persistence Behavior
Trace state is an in-memory ring. On wrap, the oldest entry advances by moving `head`. `bfa_trc_stop` prevents further trace writes, commonly after serious assertions. There is no durable persistence, but trace content is diagnostic state consumed by driver debug paths.

## Dependencies and Integration Points
The header depends on `bfad_drv.h` for kernel types, `ktime_get_ts64`, `list_head`, logging, and endian context. The 24-bit conversion helpers `bfa_hton3b` and `bfa_ntoh3b` are used by frame builders and FC id handling.

## Risks and Test Signals
Risks include raw macro manipulation of `list_head`, null or double-dequeued queue entries, callback reentrancy in wait counters, and endian-sensitive bit/byte interpretation of WWNs and FCIDs. Test signals are trace wrap/stop behavior, state transition entry actions, queue dequeue on empty and non-empty lists, wait counter zero transition, and FC id formatting on little- and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs.h

## Purpose
`bfa_defs.h` defines base BFA public data contracts: manufacturing/VPD records, status codes, booleans, adapter and IOC attributes, asynchronous event categories, PCI and ASIC identifiers, boot configuration, adapter block configuration, SFP EEPROM/diagnostic layouts, flash partition metadata, diagnostics, and PHY status/statistics.

## Important APIs and Types
The most widely consumed definitions are `enum bfa_status` and aliases `bfa_status_t`, `enum bfa_boolean`, `struct bfa_adapter_attr_s`, `struct bfa_ioc_attr_s`, `struct bfa_ioc_stats_s`, and PCI/ASIC helper macros `bfa_asic_id_cb`, `bfa_asic_id_ct`, `bfa_asic_id_ct2`, and `bfa_asic_id_ctc`. Manufacturing records include packed `struct bfa_mfg_vpd_s` and `struct bfa_mfg_block_s`, with card type macros such as `bfa_mfg_is_mezz` used by FAA validation in `bfa_core.c`. Boot-related structs include `bfa_boot_bootlun_s`, `bfa_boot_cfg_s`, `bfa_boot_pbc_s`, and `bfa_ethboot_cfg_s`.

## Control Flow and State
This header does not implement executable control flow, but it strongly shapes control decisions. Status codes distinguish retryable busy/non-operational states, unsupported features, adapter mode restrictions, invalid media, D-port and BB credit recovery failures, and firmware/config failures. ASIC id macros select hardware callback tables during IOCFC attach. Port speeds are bit-style constants consumed by FC link and RPSC conversion helpers.

## State and Persistence Behavior
Several structs mirror persistent adapter content in flash or module EEPROM. Manufacturing/VPD blocks are explicitly packed and documented as big-endian. Flash partition attributes describe persistent regions for firmware, option ROM, boot config, PBC, port config, logs, and manufacturing data. SFP structs map serial id, diagnostic, and user EEPROM pages. Boot configs persist SAN/PXE boot policy and target LUNs.

## Dependencies and Integration Points
It includes `bfa_fc.h` for WWN, MAC, SCSI LUN, port speed, and FC constants, plus `bfad_drv.h` for kernel types. It feeds IOC, flash, SFP, diagnostics, PHY, port, and adapter management modules. `bfa_core.c` uses manufacturing/card type and ASIC id helpers directly.

## Risks and Test Signals
Risks are ABI/layout drift, packed struct alignment, endian conversion omissions, duplicated or sparse status codes, and card-type logic becoming stale for new hardware. Test signals include compile-time size/layout checks where available, flash/VPD parsing with checksum failures, ASIC callback selection for all supported device ids, boot config reads, SFP diagnostic parsing, and management tooling that displays every status/state enum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_fcs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_fcs.h

## Purpose
`bfa_defs_fcs.h` defines Fibre Channel Services visible configuration, state, statistics, and attribute contracts for virtual fabrics, local ports, virtual ports, remote ports, and initiator-target nexuses. It is the management-facing companion to the wire definitions in `bfa_fc.h` and service definitions in `bfa_defs_svc.h`.

## Important APIs and Types
The header defines `enum bfa_vf_state` plus `bfa_vf_stats_s` and `bfa_vf_attr_s` for fabric login lifecycle. Local port contracts include `BFA_FCS_MAX_LPORTS`, symbolic-name structs, `enum bfa_lport_role`, `struct bfa_lport_cfg_s`, `enum bfa_lport_state`, `enum bfa_lport_type`, `enum bfa_lport_offline_reason`, `struct bfa_lport_stats_s`, and `struct bfa_lport_attr_s`. Virtual port definitions include `enum bfa_vport_state`, `bfa_vport_stats_s`, and `bfa_vport_attr_s`. Remote port and IT nexus definitions include `enum bfa_rport_state`, `enum bfa_rport_function`, `bfa_rport_stats_s`, `bfa_rport_attr_s`, `bfa_rport_remote_link_stats_s`, `bfa_rport_qualifier_s`, `enum bfa_itnim_state`, `bfa_itnim_stats_s`, and `bfa_itnim_attr_s`.

## Control Flow and State
The enums document expected FCS state machines: VF login progresses through link down, FLOGI, auth, online, EVFP, or isolation; lports move through FDISC/online/offline; vports include FDISC retry, LOGO, cleanup, and error states; rports progress through PLOGI, online, ADISC, LOGO, rediscovery, and offline paths; ITNIMs track PRLI and online/offline callbacks. Statistics counters map directly to those transitions and protocol exchanges.

## State and Persistence Behavior
Most state is runtime discovery and login state, while `bfa_lport_cfg_s` carries configured WWNs, symbolic names, roles, preboot-vport flag, and opaque application tags that can originate from persisted or preboot configuration. Attributes expose derived runtime topology, PID, fabric name, FCoE MAC, and authentication status.

## Dependencies and Integration Points
The file includes `bfa_fc.h` for protocol structs and `bfa_defs_svc.h` for port and rport QoS/service types. `bfa_fcbuild.h` consumes `enum bfa_lport_role` in PRLI and name-server registration builders. FCS modules and management paths use these structs for queries, counters, and event payloads.

## Risks and Test Signals
Risks include enum drift from actual state machines, duplicated state values in vport definitions, statistics counters not matching transitions, and role limitations that currently only expose FCP initiator. Test with FLOGI/FDISC/PLOGI/PRLI success and reject paths, NPIV unsupported/max-resource cases, RSCN rediscovery, ADISC validation, LOGO cleanup, and management queries for each state and counter block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_fcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_svc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_svc.h

## Purpose
`bfa_defs_svc.h` defines service-level configuration, attributes, and statistics for IOCFC, firmware IO and port modules, QoS, BB credit recovery, FCoE, FCP initiator throttling and IO statistics, physical port state/configuration, LUN masking, trunking, vHBA, CEE/DCBX, and AEN event payloads. It is the large shared contract between firmware, HAL modules, and management consumers.

## Important APIs and Types
Core IOCFC structs are `bfa_iocfc_intr_attr_s`, `bfa_iocfc_fwcfg_s`, `bfa_iocfc_drvcfg_s`, `bfa_iocfc_cfg_s`, `bfa_fw_iocfc_stats_s`, and `bfa_iocfc_attr_s`; these are consumed by `bfa_core.c` for memory sizing, firmware config requests, config responses, and interrupt coalescing. Statistics structs cover firmware IO, target IO, port PHY/link state machines, FIP/FCoE, LPSM, FC exchange, trunk, adapter port, MAC/CT/RDS modules, and aggregate `bfa_fw_stats_s`. Port/user-visible contracts include `bfa_port_cfg_s`, `bfa_port_attr_s`, `bfa_port_link_s`, `bfa_port_fc_stats_s`, `bfa_port_eth_stats_s`, and `bfa_port_stats_u`.

## Control Flow and State
The header defines state enums that drive management and module logic: QoS online/offline/disabled, BBCR state and error reasons, port states, port topology/opmode/link reasons, LUN mask states, FEC state, trunk state/link state, and rport AEN events. IOCFC config fields determine how many queues, IO requests, FC exchanges, unsolicited buffers, rports, task requests, SG pages, SAN boot targets, and completion queue elements are created during `bfa_cfg_get_meminfo` and `bfa_iocfc_send_cfg`.

## State and Persistence Behavior
Several structs mirror persistent or firmware-owned state: driver and firmware resource configuration, LUN mask entries, physical port config, QoS bandwidth, BB_SCN/BBCR, FAA state, path timeout, queue depth, FCoE FCF data, CEE/DCBX remote attributes, and AEN history entries. Runtime counters are volatile but represent firmware and HAL health signals.

## Dependencies and Integration Points
It includes `bfa_defs.h`, `bfa_fc.h`, and `bfi.h`, so it binds base adapter definitions, FC wire contracts, and firmware message types. `bfa.h` exposes these structs through IOCFC APIs and macros. Port, FCP, CEE, QoS, trunk, rport, and management modules use these definitions for ioctl/sysfs/netlink-style reporting.

## Risks and Test Signals
Risks include ABI instability, packed layout mismatch, endian mistakes in fields marked `__be16`, duplicated `MAX_LUN_MASK_CFG`, large stats structs drifting from firmware, and config values exceeding firmware limits. Test signals are firmware config negotiation, interrupt coalescing set/get, queue depth/path timeout limits, LUN mask min-config behavior, port state/link reason reporting, QoS/BBCR transitions, FCoE/CEE stats, and AEN queue population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_defs_svc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fc.h

## Purpose
`bfa_fc.h` is the Fibre Channel protocol wire-format header. It defines packed frame headers, ELS/BLS payloads, login/service parameter layouts, FCP command and response IUs, CT generic service headers, name-server and management-server request/response payloads, FDMI records, well-known addresses, timeout constants, virtual fabric tags, speed enums, and utility types such as `wwn_t`, `mac_t`, and `fc_symname_s`.

## Important APIs and Types
Foundational structs include `struct fchs_s` for FC frame headers, `fc_els_cmd_s`, `fc_logi_s`, `fc_logo_s`, `fc_adisc_s`, `fc_prli_s`, `fc_prlo_s`, `fc_scr_s`, `fc_ls_rjt_s`, `fc_rrq_s`, `fc_ba_acc_s`, `fc_tprlo_s`, `fc_rscn_pl_s`, `fc_rnid_*`, `fc_rpsc*`, `fcp_cmnd_s`, `fcp_resp_s`, `ct_hdr_s`, FC-GS name-server structs, GMAL/GFN structs, and FDMI attribute/register structs. Enums and macros define routing, category, FC types, frame-control bits, ELS opcodes, PDU size bounds, LS reject reasons, CT responses/reasons, FC-GS commands, FC classes, FCP IO directions, and task management flags.

## Control Flow and State
This header has no executable flow, but its field layouts are consumed by `bfa_fcbuild.c` to construct login, discovery, name-server, management-server, accept, and reject frames. Parse helpers validate these layouts by checking command codes, PRLI response codes, target/initiator bits, PLOGI class validity, receive size ranges, and WWN identity.

## State and Persistence Behavior
The data is primarily transient wire state. Some fields represent persistent identifiers or management information, including WWNs, symbolic names, FDMI HBA/port attributes, RNID topology data, fabric names, and management addresses. Packed layout and bitfield endian branches are part of the on-wire ABI and must remain stable.

## Dependencies and Integration Points
It depends on `bfad_drv.h` for Linux integer, endian, `BIT`, and SCSI LUN types. It is included by base definitions, FCS definitions, and frame-building code. Fibre Channel control modules use it to interpret unsolicited frames and build FCXP payloads.

## Risks and Test Signals
Risks include bitfield layout differences across endian/compilers, missing byte-order conversion for 24-bit IDs or `__be*` fields, flexible array sizing mistakes, duplicated RNID associated-type macros, and unsafe payload length assumptions. Test signals include protocol frame golden tests for ELS, BLS, CT, FCP, RSCN, RNID, RPSC, FDMI, and name-server packets on little- and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.c

## Purpose
`bfa_fcbuild.c` implements Fibre Channel link-service, basic-link-service, CT generic-service, name-server, management-server, and FDMI frame construction helpers plus a few response parsers. It turns the wire structs from `bfa_fc.h` into initialized FC headers and payloads used by FCS/login/discovery modules.

## Important APIs and Functions
`fcbuild_init` initializes static templates for ELS requests/responses, BLS responses, BA_ACC, PLOGI, PRLI, RRQ, and FCP headers. Public builders include FLOGI/PLOGI/PLOGI ACC, PRLI/PRLI ACC, LOGO/LOGO ACC, ADISC/ADISC ACC, LS_ACC/LS_RJT, BA_ACC, PRLO ACC, RNID ACC, RPSC2, RPSC ACC, SCR, GID_PN, GPN_ID, GID_FT, RFT_ID, RFF_ID, RSPN_ID, RSNN_NN, RNN_ID, GS reject, FDMI request header, GMAL, and GFN. Parsers include `fc_plogi_parse`, `fc_prli_rsp_parse`, `fc_adisc_rsp_parse`, and `fc_logout_params_pages`.

## Control Flow and State
Most functions copy a prebuilt template or zero a payload, fill destination/source IDs, exchange IDs, command codes, and protocol fields, then return the payload length. ELS request and response builders centralize header setup; CT helpers centralize generic-service headers. `fc_plogi_x_build` handles both PLOGI request and accept by switching on ELS code. Name-server helpers build CT payloads after setting the FC header to the well-known name server; management helpers target the management server.

## State and Persistence Behavior
The file holds static in-memory templates initialized once by `fcbuild_init`; callers depend on that initialization before building frames. It does not persist state, but constructed payloads carry persistent identity data such as WWNs, symbolic names, FC4 feature registration, RNID topology records, and management-server WWN queries.

## Dependencies and Integration Points
It depends on `bfa_fcbuild.h`, `bfa_fc.h`, `bfa_defs_fcs.h`, common endian helpers, and string helpers from the driver environment. FCS modules use these builders when sending FCXP exchanges for fabric login, port login, discovery, name-server registration, RSCN registration, speed reporting, and management queries.

## Risks and Test Signals
Risks include missing `fcbuild_init`, endian mistakes around IDs/exchange ids, insufficient buffer sizing for variable-length PRLO/TPRLO/RPSC2/FDMI payloads, unchecked name truncation, role parameters ignored in some builders, and limited parser validation. Test with golden packet byte comparisons, invalid PLOGI/PRLI/ADISC responses, name truncation, multiple PRLO pages, RPSC2 pid counts, and all well-known address builders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.h

## Purpose
`bfa_fcbuild.h` declares the FC frame-building/parsing API implemented by `bfa_fcbuild.c` and provides small protocol utility helpers. It is the interface FCS and login/discovery modules use to construct ELS, BLS, CT, name-server, management-server, FDMI, and logout frames.

## Important APIs and Types
Utility macros and inlines include `wwn_is_equal`, `fc_roundup`, `fc_get_ctresp_pyld_len`, `fc_rpsc_operspeed_to_bfa_speed`, and `fc_bfa_speed_to_rpsc_operspeed`. `enum fc_parse_status` standardizes parser results beyond simple success/failure for length, accept, WWN, receive-size, FCP type, and process-associator validation failures. `struct fc_templates_s` names the major frame templates. Declarations cover all frame builders for FLOGI/PLOGI/PRLI/ADISC/LOGO/SCR/RNID/RPSC/name-server/FDMI/GMAL/GFN/BA_ACC/PRLO/TPRLO plus parser APIs.

## Control Flow and State
Callers generally allocate or point to an FC header and payload buffer, call the relevant builder, transmit the returned byte count through an FC exchange, then parse the response with the matching parser where one exists. Speed conversion helpers bridge `enum bfa_port_speed` from service definitions and RPSC on-wire speed values from `bfa_fc.h`.

## State and Persistence Behavior
The header itself owns no mutable state. It exposes `fcbuild_init`, which initializes static templates inside the implementation. Frame builders carry identity/configuration state supplied by callers, such as WWNs, PIDs, symbolic names, roles, FC4 features, and speed info.

## Dependencies and Integration Points
It includes `bfad_drv.h`, `bfa_fc.h`, and `bfa_defs_fcs.h`, binding Linux driver types, wire-format structs, and FCS role definitions. The API is a narrow integration point between higher-level FCS state machines and lower-level FCXP send paths.

## Risks and Test Signals
Risks include callers passing undersized payload buffers, forgetting `fcbuild_init`, mismatch between declared builders and implementation coverage, ambiguous endian expectations for `u16` versus `__be16` exchange IDs, and parse statuses not being handled distinctly. Test signals include compile coverage for every declared builder, golden frame fixtures, speed conversion round-trips, response length underflow for `fc_get_ctresp_pyld_len`, and negative parser status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcbuild.h -->
