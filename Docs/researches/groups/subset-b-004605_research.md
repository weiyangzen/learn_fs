# Research: subset-b-004605

This grouped report covers the QED management firmware control path and its firmware shared-memory interface. Each section is source-tree aligned and can be split into the required per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.c

## Purpose

`qed_mcp.c` implements the QED driver's runtime interface to the management firmware, called MCP or MFW. It discovers the firmware shared-memory layout, maintains the PF-specific driver mailbox, sends serialized driver-to-MFW commands, consumes MFW-to-driver event bits, and translates firmware HSI structures into driver state. The file is the operational bridge between the Linux QED core and firmware-owned functions such as load arbitration, link configuration, transceiver reads, NVM access, VF FLR notifications, resource allocation, BIST, crash-dump acknowledgements, and management lockdown status.

The implementation assumes a PF context for most operations. Several helpers reject VFs with `-EINVAL`, while `qed_mcp_get_mfw_ver()` has a VF-specific path that returns the version cached in the PF/VF acquire response.

## Important APIs and Functions

The mailbox core is built around `qed_mcp_cmd_and_union()`, `_qed_mcp_cmd_and_union()`, `qed_mcp_cmd()`, `qed_mcp_cmd_nosleep()`, `qed_mcp_nvm_rd_cmd()`, and the internal `qed_mcp_nvm_wr_cmd()`. Callers provide a command, parameter, optional `union drv_union_data` source and destination buffers, and sleepability flags. The command path validates MFW initialization, refuses commands after a severe MFW response timeout unless `QED_MB_FLAG_AVOID_BLOCK` was used, enforces union data size limits, serializes access with `cmd_lock`, increments the mailbox sequence, writes `drv_mb_param`, `union_data`, and `drv_mb_header`, then polls `fw_mb_header` until the matching sequence arrives.

Initialization and lifetime are handled by `qed_mcp_cmd_init()`, `qed_load_mcp_offsets()`, `qed_mcp_cmd_port_init()`, `qed_mcp_reread_offsets()`, `qed_mcp_free()`, and `qed_mcp_is_init()`. `qed_load_mcp_offsets()` reads `MISC_REG_SHARED_MEM_ADDR`, converts it into the MCP GRC window with `GRCBASE_MCP`, discovers `PUBLIC_MFW_MB` and `PUBLIC_DRV_MB` using HSI section offsize descriptors, waits up to one second for `public_mfw_mb.sup_msgs` to become nonzero, seeds `drv_mb_seq` and `drv_pulse_seq`, and stores the reset-history register. `qed_mcp_reread_offsets()` detects an MCP reset via `MISCS_REG_GENERIC_POR_0` and refreshes shared-memory offsets.

Load and unload are handled by `qed_mcp_load_req()`, `__qed_mcp_load_req()`, `qed_mcp_cancel_load_req()`, `qed_mcp_load_done()`, `qed_mcp_unload_req()`, and `qed_mcp_unload_done()`. Load request payloads include driver/MFW HSI version, firmware version, build-time feature bitmap, driver role, timeout, force-load policy, and avoid-engine-reset flag. The code retries with HSI version 1 for old MFW, may issue force load only when policy and existing driver role allow it, and cancels load if a force would disrupt active PFs. Unload sets a bypass bit so event processing is skipped while the driver waits for in-flight MFW event handling to drain.

Link management is implemented by `qed_mcp_set_link()`, `qed_mcp_handle_link_change()`, `qed_mcp_read_eee_config()`, and accessors `qed_mcp_get_link_params()`, `qed_mcp_get_link_state()`, and `qed_mcp_get_link_capabilities()`. The driver converts `qed_mcp_link_params` into `struct eth_phy_cfg`, including speed, pause, loopback, EEE, base FEC, extended speeds, and extended FEC. Link-change events read `public_port.link_status`, optionally virtual-link state from `public_func.status`, update bandwidth, derive speed/duplex/autoneg/partner pause/FEC/EEE state, call rate configuration helpers, then notifies the rest of the driver through `qed_link_update()`.

Event dispatch is centralized in `qed_mcp_handle_events()`. It reads MFW message bytes from `public_mfw_mb.msg`, compares them to `mfw_mb_shadow`, skips processing during unload bypass, handles changed message IDs, writes acknowledgements back in big-endian format, and updates the shadow. It dispatches link changes, VF FLR notifications, LLDP/DCBX updates, UFP/OEM configuration, transceiver state changes, error recovery, protocol stats requests, bandwidth and S-tag updates, fan failure, critical errors, and TLV requests.

NVM and transceiver helpers include `qed_mcp_nvm_read()`, `qed_mcp_nvm_write()`, `qed_mcp_nvm_resp()`, `qed_mcp_phy_sfp_read()`, `qed_mcp_bist_*()`, `qed_mcp_nvm_info_populate()`, `qed_mcp_nvm_info_free()`, `qed_mcp_get_nvm_image_att()`, `qed_mcp_get_nvm_image()`, `qed_mcp_nvm_get_cfg()`, and `qed_mcp_nvm_set_cfg()`. Reads and writes are chunked by `MCP_DRV_NVM_BUF_LEN` or `MAX_I2C_TRANSACTION_SIZE` and use firmware responses to track NVM command status. Successful NVM writes invalidate `p_hwfn->nvm_info`.

Other externally visible operations cover firmware version reads, media and board configuration, process-kill recovery, VF MSI-X provisioning, MCP reset/halt/resume, out-of-band management updates for MAC/MTU/WoL/eswitch/driver state, LED control, parity masking, resource allocation, generic MFW resource locking, feature negotiation, engine-affinity and PPFID bitmap reads, raw debug-data streaming, and ESL management status.

## Control Flow

The normal PF initialization flow allocates `qed_mcp_info`, initializes spinlocks and command list state, discovers SHMEM mailbox offsets, allocates current and shadow MFW event buffers, initializes port shared-memory address, negotiates capabilities, reads function info from SHMEM, sends load request, sets driver capabilities, configures link, and eventually sends load-done. Runtime command flow is strictly serialized through `cmd_lock` even though the command list supports tracking by sequence number. Before sending a new command, `_qed_mcp_cmd_and_union()` checks whether a pending command has completed by sampling `fw_mb_header`; if it cannot clear the previous command within `QED_DRV_MB_MAX_RETRIES`, it returns `-EAGAIN`.

On MFW response timeout, the code logs MCP CPU mode/state/program counter samples, removes the pending command, optionally sets `b_block_cmd`, and raises `QED_HW_ERR_MFW_RESP_FAIL`. This creates a persistence boundary: after the first severe command timeout, future mailbox commands fail fast with `-EBUSY` until `qed_mcp_resume()` clears the block state.

Event handling follows a shadow-diff model. The MFW exposes a compact message array; each changed byte position is a message type. The handler processes each changed slot, then writes a full acknowledgement array and copies the current message buffer to the shadow. During unload, `QED_MCP_BYPASS_PROC_BIT` prevents new event work from starting, while `QED_MCP_IN_PROCESSING_BIT` lets unload wait briefly for a handler already in progress.

Resource locking has a separate firmware opcode protocol layered over `DRV_MSG_CODE_RESOURCE_CMD`. `qed_mcp_resc_lock_default_init()` sets sane retry and aging behavior, `qed_mcp_resc_lock()` retries `RESOURCE_OPCODE_REQ*` until granted or retries are exhausted, and `qed_mcp_resc_unlock()` maps release, force-release, wrong-owner, and already-released responses.

## State and Persistence Behavior

Persistent driver-side state lives mostly in `struct qed_mcp_info` under `p_hwfn->mcp_info`: SHMEM bases, mailbox addresses, command sequence, pulse sequence, link input/output/capabilities, function info, event shadow buffers, MFW capabilities, debug-data sequence, and command/event synchronization bits. The code also updates `p_hwfn->nvm_info`, `p_hwfn->hw_info`, `p_hwfn->ufp_info`, `p_hwfn->qm_info`, `p_hwfn->cdev->wol_config`, `p_hwfn->cdev->wol_mac`, `p_hwfn->cdev->recov_in_prog`, `p_hwfn->cdev->mcp_nvm_resp`, `p_hwfn->cdev->fir_affin`, `p_hwfn->cdev->l2_affin_hint`, and `p_hwfn->cdev->ppfid_bitmap`.

Firmware-facing persistence is mediated through the MCP scratchpad and NVM. The code reads and writes `public_drv_mb`, `public_mfw_mb`, `public_port`, `public_func`, `public_global`, NVM image directories, and NVM configuration options. NVM writes are durable from the hardware perspective and therefore chunked, response-checked, and surfaced through `mcp_nvm_resp`.

## Dependencies and Integration Points

This file depends on the HSI definitions in `qed_mfw_hsi.h`, driver declarations in `qed_mcp.h`, register access helpers from `qed_hw.h`, register constants from `qed_reg_addr.h`, SR-IOV helpers from `qed_sriov.h`, DCBX integration from `qed_dcbx.h`, context/resource definitions from `qed_cxt.h`, and common device state in `qed.h`. It calls broader QED subsystems for link update, bandwidth shaping, VF scheduling, DCBX MIB updates, UFP/stag slowpath updates, recovery scheduling, hardware error notification, PTT acquisition, and NVM image consumers.

The file is tightly coupled to firmware HSI bit definitions and assumes that `union drv_union_data` is the maximum mailbox payload. It also contains endianness handling specific to MFW SHMEM: MFW-to-driver event bytes are read as big-endian dwords, acknowledgements are written as big-endian, and MAC update payloads are packed in native dword order to match firmware interpretation after PCI swaps.

## Risks and Edge Cases

The highest-risk area is mailbox sequencing and timeout behavior. A missed or stale sequence blocks subsequent commands, and a full response timeout can set `b_block_cmd`, causing later operations to fail until explicit resume. Shared-memory offsets may change after MCP reset; `qed_mcp_reread_offsets()` mitigates this but only on command paths that call it.

Input-size validation protects union mailbox transfers, but multiple public APIs cast byte buffers to `u32 *` for NVM/transceiver transfers. These paths rely on small firmware transfer sizes and caller-provided buffers being suitable for dword access. In `qed_mcp_nvm_rd_cmd()`, the code copies `*o_txn_size` bytes from a fixed `MCP_DRV_NVM_BUF_LEN` stack buffer; correctness depends on the MFW returning a sane transaction size.

Event handling acknowledges all message dwords after processing, even if a particular message type was unimplemented or returned an error. That matches the driver contract but means diagnostics must rely on logs rather than retrying the same MFW event. Link handling also replays a synthetic link-change after `qed_mcp_set_link()`, which is necessary for old firmware but can expose ordering assumptions around link initialization and bandwidth programming.

NVM writes alter durable device state and invalidate the cached image table. Resource locking depends on firmware ownership and timeout semantics; callers must initialize lock params correctly and inspect `b_granted` or `b_released` rather than assuming success means ownership.

## Test Signals

Useful test and instrumentation signals include DP logs for mailbox command/response pairs, MCP CPU state dumps on timeout, load-refusal and force-load decisions, link status decoding, NVM response codes saved in `cdev->mcp_nvm_resp`, BIST return codes, resource lock owner/opcode fields, MFW capability bitmasks, and event-handler "old CMD/new CMD" traces. Hardware or simulator tests should cover old-HSI load fallback, MFW timeout and block behavior, MCP reset offset reread, link up/down with virtual link capability, VF FLR ack clearing, NVM chunked read/write, unsupported MFW commands, resource lock busy/grant/release paths, and ESL status reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.h

## Purpose

`qed_mcp.h` is the driver-facing declaration layer for the QED management firmware interface implemented in `qed_mcp.c`. It defines the stable in-driver data structures used to configure link state, expose function information, pass protocol statistics and TLVs, perform mailbox commands, and coordinate resource locks. It also declares the public MCP APIs used by the rest of the QED core, ethernet, storage offload, RDMA, SR-IOV, debug, and management paths.

The header does not define the firmware scratchpad wire layout itself; it includes `qed_mfw_hsi.h` indirectly through implementation use and includes `qed_hsi.h` and `qed_dev_api.h` for driver-visible enums and hardware abstractions. Its role is to hide most firmware mailbox details behind QED-native types while still exposing enough state for initialization and fast-path-adjacent link updates.

## Important Types and API Groups

Link configuration is represented by `struct qed_mcp_link_speed_params`, `struct qed_mcp_link_pause_params`, `enum qed_mcp_eee_mode`, `struct qed_mcp_link_params`, `struct qed_mcp_link_capabilities`, and `struct qed_mcp_link_state`. These types split desired input (`link_input` in `qed_mcp_info`) from firmware-reported output (`link_output`) and default capabilities. They cover base and extended advertised speeds, forced speed, pause autoneg/forced RX/TX, loopback, EEE, FEC, line speed, PF rate after bandwidth constraints, duplex, autoneg completion, PFC, link partner capabilities, SFP fault, EEE advertisements, and active FEC mode.

`struct qed_mcp_function_info` is the driver's cached view of per-PF firmware configuration: pause-on-host, PCI personality, min/max bandwidth, MAC, FCoE WWNs, outer VLAN/stag, and MTU. It is populated from `public_func` shared memory by `qed_mcp_fill_shmem_func_info()`.

Firmware reporting and management data structures include `struct qed_mcp_drv_version`, per-protocol stats structures, `union qed_mcp_protocol_stats`, `enum qed_mcp_protocol_type`, TLV enums and `union qed_mfw_tlv_data`, NVM config flags, and `struct qed_nvm_image_att`.

`struct qed_mcp_info` is the central runtime state container. It owns the pending command list, `cmd_lock`, command blocking flag, `link_lock`, SHMEM section addresses, mailbox sequence state, link input/output/capabilities, cached function info, event current/shadow buffers, MFW message length, MCP reset history, negotiated capability bitmask, atomic debug-data sequence, `unload_lock`, and event handling status bits. `QED_MCP_BYPASS_PROC_BIT` and `QED_MCP_IN_PROCESSING_BIT` coordinate unload with event handling.

`struct qed_mcp_mb_params` is the generic command descriptor for mailbox transactions. It carries command, parameter, optional source and destination union payload pointers, payload sizes, response fields, and flags. `QED_MB_FLAG_CAN_SLEEP` selects sleepable polling, while `QED_MB_FLAG_AVOID_BLOCK` prevents a command failure from globally blocking future mailbox commands.

Resource locking declarations include `enum qed_resc_lock`, `struct qed_resc_lock_params`, `struct qed_resc_unlock_params`, retry/timeout defaults, and APIs for lock, unlock, default initialization, resource allocation reads, and resource max updates. The resource lock range intentionally maps to firmware generic resource IDs 0..31, with debug dump and per-port PTP locks plus a resource-allocation lock.

## Public API Surface

The header declares initialization and mailbox primitives (`qed_mcp_cmd_init()`, `qed_mcp_cmd_port_init()`, `qed_mcp_free()`, `qed_mcp_is_init()`, `qed_mcp_cmd()`, `qed_mcp_cmd_nosleep()`, `qed_mcp_nvm_rd_cmd()`, `qed_mcp_reset()`, `qed_mcp_read_mb()`, `qed_mcp_handle_events()`), lifecycle operations (`qed_mcp_load_req()`, `qed_mcp_load_done()`, `qed_mcp_unload_req()`, `qed_mcp_unload_done()`), link and media operations (`qed_mcp_set_link()`, link accessors, MFW/MBI version reads, media/transceiver/board config reads), and management updates (`qed_mcp_ov_update_*()`, `qed_mcp_set_led()`, `qed_mcp_mask_parities()`).

NVM and diagnostics APIs include `qed_mcp_nvm_read()`, `qed_mcp_nvm_write()`, `qed_mcp_nvm_resp()`, image attribute/image read helpers, BIST helpers, NVM info cache populate/free, NVM config get/set, mdump retained data access, and raw debug data send. SR-IOV and recovery APIs include VF FLR ack, VF MSI-X configuration, PF FLR initiation, process kill counter read, recovery trigger, and recovery prolog. Capability and platform APIs include MFW feature get/set, SmartAN support, extended speed support inline check, UFP config read, engine affinity, PPFID bitmap, enhanced system lockdown support, and ESL active status.

## Control Flow and State Contract

The header encodes the expected call order. A PF creates `qed_mcp_info` with `qed_mcp_cmd_init()`, initializes port address after port mapping is known, reads capabilities and function information, performs load request/done, then uses link, NVM, event, and management APIs during runtime. Callers that only need current state retrieve pointers to `link_input`, `link_output`, or `link_capabilities`; these are owned by `qed_mcp_info` and must not outlive it.

Command callers either use the simple `qed_mcp_cmd()`/`qed_mcp_cmd_nosleep()` wrappers or the more specialized APIs that construct `qed_mcp_mb_params` internally. The `qed_mcp_mb_params` contract is size-bound by `union drv_union_data`, so source and destination payloads are small mailbox payloads rather than arbitrary DMA buffers.

Resource lock callers should use `qed_mcp_resc_lock_default_init()` to initialize retry and aging behavior, then check result booleans in the parameter structures. A zero return from `qed_mcp_resc_lock()` means the firmware protocol completed, not necessarily that the lock was granted.

## Dependencies and Integration Points

This header is included across QED core modules that need MFW services. It depends on Linux primitives (`types`, `delay`, `slab`, `spinlock`), protocol TLV definitions from `linux/qed/qed_fcoe_if.h`, QED hardware/software interface definitions from `qed_hsi.h`, and common device API types from `qed_dev_api.h`. The declarations reference `struct qed_hwfn`, `struct qed_ptt`, `struct qed_dev`, firmware HSI structs such as `bist_nvm_image_att` and `mdump_retain_data_stc`, and QED enums such as `qed_led_mode`, `qed_resources`, `qed_nvm_images`, and `qed_override_force_load`.

The `MCP_PF_ID_BY_REL()` macro is a notable integration point with hardware mode. It maps relative PF IDs to MCP PF IDs differently for BB devices, incorporating the hardware function's absolute PF parity in CMT mode. Incorrect use of `rel_pf_id` without this macro would address the wrong shared-memory PF slot.

## Risks and Edge Cases

Because `qed_mcp_info` is exposed in the header, non-MCP modules can access internal state directly if they include the header. That makes lock discipline important: command list and mailbox state require `cmd_lock`, link state updates require `link_lock`, and unload/event status bits require `unload_lock`.

Several comments in the header contain stale wording, for example `qed_mcp_cmd()` says polling is checked every 10 ms even the implementation uses 10 microsecond intervals with sleep ranges. Consumers should trust implementation constants for timing-sensitive behavior.

The public state accessors return raw pointers, not copies. Callers must handle NULL when MCP is not initialized and avoid unsynchronized mutation except through established QED paths. NVM and management update APIs can alter durable firmware/device state, so tests and callers need to distinguish read-only query helpers from persistent configuration operations.

## Test Signals

Header-level validation is mostly compile-time and integration-oriented: all declared APIs should match implementation signatures; feature flags should map to firmware HSI definitions; and structure sizes used in mailbox payloads must not exceed `union drv_union_data`. Runtime tests should validate initialization order, NULL-safe accessors, MCP PF ID mapping in BB/CMT mode, resource-lock parameter defaults, extended-speed feature gating, and expected error behavior for VF contexts or uninitialized MCP state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mfw_hsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mfw_hsi.h

## Purpose

`qed_mfw_hsi.h` defines the host software interface shared by the QED driver and management firmware. It is a firmware ABI header: scratchpad section descriptors, public shared-memory layouts, mailbox command and response codes, event message IDs, NVM image metadata, link/media bitfields, DCBX/LLDP data structures, TLV IDs, and persistent NVM configuration structures are all described here. `qed_mcp.c` relies on these definitions to locate firmware-owned shared memory and to pack or decode mailbox payloads.

The file is intentionally data-heavy and has little executable logic. Its correctness depends on exact structure layout, bit masks, offsets, and enum values matching the MFW image that owns the MCP scratchpad and NVM directory.

## Important Layouts and Types

Scratchpad addressing is based on `offsize_t` and macros `SECTION_OFFSET()`, `QED_SECTION_SIZE()`, `SECTION_ADDR()`, and `SECTION_OFFSIZE_ADDR()`. Offsets and sizes are encoded in dwords, then converted to byte addresses under `MCP_REG_SCRATCH`. `struct mcp_public_data` contains the public SHMEM sections used by the driver: per-PF driver mailboxes, per-PF MFW mailboxes, global data, path data, port data, and function data.

`struct public_drv_mb` is the driver-to-firmware mailbox. It contains `drv_mb_header`, `drv_mb_param`, `fw_mb_header`, `fw_mb_param`, pulse mailboxes, and `union drv_union_data`. Header fields split sequence numbers from command or response codes. `union drv_union_data` is the bounded inline payload for link configuration, WOL MAC, raw NVM/debug data, stats, resource info, BIST image attributes, load request/response, mdump retain data, attribute writes, LLDP stats, PCIe stats, and trace filters.

`struct public_mfw_mb` is the firmware-to-driver event channel. It exposes `sup_msgs`, a packed message array, and a matching acknowledgement array. `enum MFW_DRV_MSG_TYPE` defines event slots such as link change, VF disabled, LLDP/DCBX updates, recovery, bandwidth update, S-tag update, protocol stats requests, fan/temperature failure, transceiver state, critical error, TLV request, OEM configuration, generic IDC, and debug dump requests.

`struct public_global`, `struct public_path`, `struct public_port`, and `struct public_func` are the main shared-memory records consumed by the driver. Global fields include path/port counts, CMT teaming, temperatures, MFW version, running bundle, BMC/NCSI counters, and device attributes. Path fields include VF FLR disabled bitmap and process-kill counter. Port fields include link status, PHY configuration address, media type, LLDP/DCBX MIBs, transceiver data, EEE status, OEM/UFP config, pause flood monitor, NIG counters, and traffic class counters. Function fields include MTU, MSI-X count, function protocol/bandwidth config, virtual-link status, MAC, FCoE WWNs, outer VLAN/stag, VF-disabled ACK bitmap, driver ID, OEM function config, and driver version.

Link and PHY definitions include `struct eth_phy_cfg`, speed/autoneg constants, pause bits, loopback modes, EEE config, base FEC, extended FEC, and extended speed advertisement fields. Link state bits in `public_port.link_status` encode link up, speed/duplex, autoneg, PFC, partner advertised speeds, flow control, SFP fault, signal/fault flags, FEC active mode, and external PHY link state.

NVM definitions include `struct nvm_cfg1_glob`, `struct nvm_cfg1_port`, `struct nvm_cfg1_func`, `struct nvm_cfg1`, `struct nvm_cfg`, scratchpad/static-init descriptors, NVM image directory structures, VPD image format, hardware-set images, and NVM metadata binary option records. `enum nvm_image_type` maps image IDs such as MFW bundles, NVM_CFG1, default config, mdump, iSCSI/FCoE configs, PHY firmware, recovery, PLDM, key-certificate images, hardware dump, and idle check.

Mailbox command definitions are in `enum drv_msg_code_enum`; responses are in `enum fw_msg_code_enum`. Parameter masks describe NVM chunk offsets/sizes, VF MSI-X configuration, management updates, unload WOL modes, resource allocation protocol versions, BIST subcommands, feature support advertisement, transceiver I2C reads, NVM config options, debug data size, engine affinity, PPFID bitmap, and management lockdown status.

## Control Flow Implied by the HSI

The driver first reads the public section table from the MCP scratchpad, then uses section offsize descriptors to locate the PF, port, path, and global records relevant to its hardware function. It sends commands by writing `union_data`, `drv_mb_param`, and `drv_mb_header` with a new sequence number, then polls for `fw_mb_header` with the same sequence and a firmware response code. MFW events flow in the opposite direction through `public_mfw_mb.msg` and are acknowledged by copying observed message dwords into `public_mfw_mb.ack`.

Load arbitration uses `struct load_req_stc` and `struct load_rsp_stc` with driver role, lock timeout, force-load request, avoid-reset flag, existing driver version, firmware version, MFW HSI version, and driver-exists flag. Link setup uses `struct eth_phy_cfg`, while link indications are read from `public_port.link_status` and virtual link is read from `public_func.status`.

Persistent NVM operations use small mailbox payloads and parameter-encoded offsets/sizes. Larger semantic objects such as complete NVM images are discovered through BIST image attributes and NVM directory metadata, then read in chunks by the MCP implementation.

## State and Persistence Behavior

The HSI represents three state classes. Runtime volatile state lives in the MCP scratchpad public data: mailboxes, event bits, link state, DCBX/LLDP MIBs, process-kill counters, UFP/OEM settings, and function configuration reflected by firmware. Durable state lives in NVM image structures and `nvm_cfg1` configuration records. Diagnostic state spans MFW trace buffers, mdump retained data, debug-data mailbox payloads, hardware dump image types, and trace module metadata.

Because the header is the ABI contract, field additions are append-oriented and many structures include reserved arrays. Drivers must use advertised capabilities and response codes rather than assuming all fields or commands are supported by every MFW revision.

## Dependencies and Integration Points

This header assumes QED register constants such as `MCP_REG_SCRATCH`, `CPU_SPAD_BASE`, and `STATIC_INIT_BASE`, kernel integer types, `BIT()`, and common field macros supplied by surrounding QED/Linux includes. It is consumed directly by `qed_mcp.c` and indirectly by DCBX, NVM, debug, SR-IOV, link, and management code. It integrates firmware protocol with Linux-visible operations such as ethtool NVM access, devlink-style diagnostics, link settings, WoL, VF provisioning, and hardware recovery.

The TLV enum is an integration contract with management reporting. It spans device properties, configuration, port data, function data, FCoE, iSCSI, PCIe error reporting, NCSI counters, and RDMA driver version reporting.

## Risks and Edge Cases

The main risk is ABI drift. A changed mask, enum value, structure packing assumption, or section size can cause the driver to read the wrong shared-memory field or send a malformed mailbox payload. Since many fields are bit-packed, field macros must be used consistently and caller code must mask/shift with the HSI definitions rather than open-coded constants.

Endianness is subtle. Some mailbox event data is treated as big-endian by MFW, while normal register reads return host-order dwords after bus semantics. `qed_mcp.c` handles this explicitly for MFW messages and driver version/MAC payloads; new users of this header need to preserve those conventions.

Compatibility is also a concern. Older MFW may not support HSI version 2 load requests, feature-support commands, resource allocation versions, BIST image enumeration, debug-data send, engine config, PPFID bitmap, or enhanced system lockdown. The driver must handle `FW_MSG_CODE_UNSUPPORTED`, old-HSI refusal, and absent capability bits gracefully.

NVM structures describe durable firmware storage. Incorrect offsets, lengths, or directory sequence handling can corrupt firmware images or configuration. Tests and tooling should treat write paths as high risk and prefer read-only validation unless running in a controlled hardware lab.

## Test Signals

HSI validation signals include compile-time structure availability, command/response numeric matching with MFW documentation, SHMEM section size sanity, `sup_msgs` readiness, link status decode correctness for each speed/FEC/media combination, load request fallback behavior, unsupported-command handling, NVM image directory parsing, event ack writes, and feature bit negotiation. Hardware tests should exercise multiple MFW revisions to catch ABI drift and confirm that reserved/extended fields remain backward compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mfw_hsi.h -->
