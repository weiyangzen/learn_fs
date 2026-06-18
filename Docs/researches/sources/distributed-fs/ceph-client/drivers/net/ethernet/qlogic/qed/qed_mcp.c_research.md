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
