# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_mgmt.c

## Purpose

`be_mgmt.c` implements management-plane firmware commands for the `be2iscsi` driver. It builds embedded and non-embedded MCC/mailbox requests for vendor BSG flash operations, TCP connect-and-offload, EQ delay tuning, initiator-name lookup, network interface IP/gateway/DHCP/VLAN configuration, NIC configuration lookup, firmware boot-session discovery/logout/reopen, connection invalidation/upload, ICD invalidation for SCSI error handling, and generation-specific iSCSI target-context-update WRB construction.

## Important APIs And Functions

Externally used functions include `mgmt_vendor_specific_fw_cmd`, `mgmt_open_connection`, `beiscsi_modify_eq_delay`, `beiscsi_get_initiator_name`, `beiscsi_if_get_handle`, `beiscsi_if_set_gw`, `beiscsi_if_get_gw`, `beiscsi_if_en_static`, `beiscsi_if_en_dhcp`, `beiscsi_if_set_vlan`, `beiscsi_if_get_info`, `mgmt_get_nic_conf`, boot helpers (`beiscsi_boot_logout_sess`, `beiscsi_boot_reopen_sess`, `beiscsi_boot_get_sinfo`, `__beiscsi_boot_get_shandle`, `beiscsi_boot_get_shandle`), sysfs display helpers, `beiscsi_offload_cxn_v0`, `beiscsi_offload_cxn_v2`, `beiscsi_invalidate_cxn`, `beiscsi_upload_cxn`, and `beiscsi_mgmt_invalidate_icds`.

Shared internal helpers provide the common non-embedded command pattern:

- `beiscsi_prep_nemb_cmd` allocates coherent DMA memory, sets size, and prepares the firmware header.
- `beiscsi_exec_nemb_cmd` allocates an MCC WRB under `mbox_lock`, attaches the non-embedded SGE, optionally records an async callback and DMA buffer ownership in the MCC tag state, notifies firmware, and waits for completion for synchronous commands.
- `beiscsi_free_nemb_cmd` frees the DMA command buffer unless ownership was deferred because the firmware/MCC path is busy.
- `__beiscsi_eq_delay_compl` handles async EQ delay completion and frees stored DMA memory.

Network functions manipulate the firmware iSCSI interface by retrieving the interface handle, clearing existing static IPs, releasing DHCP state, setting static IP/subnet, enabling DHCP, deleting/adding default gateways, setting VLAN through `be_cmd_set_vlan`, and fetching interface/NIC configuration. Boot functions operate as an async state machine coordinated with `be_main.c` boot work.

## Control Flow

Management command flow usually allocates a DMA command buffer, populates request fields, posts an MCC WRB, waits for or registers a completion, copies response data when needed, and frees the DMA buffer. `mgmt_open_connection` is invoked by endpoint connect logic: it validates address family, resolves the ULP/default header/data queues for the endpoint CID, builds `OPCODE_COMMON_ISCSI_TCP_CONNECT_AND_OFFLOAD`, assigns a completion queue in round-robin order, records endpoint destination address/port/type, sets template PDU address and queue IDs, and posts the command. For non-BE2/BE3 adapters it uses command version 1 and TCP window parameters.

Interface configuration flows are deliberately ordered. `beiscsi_if_en_static` gets current interface info, releases DHCP if active, clears any existing IP, then sets the provided static IP unless the call only wanted DHCP release. `beiscsi_if_en_dhcp` gets current interface info, returns if DHCP is already active, clears static IP, deletes gateway configuration, then posts a blocking DHCP configuration request. `beiscsi_if_set_gw` reads existing gateway, deletes it if nonzero, then adds the new gateway.

Boot-session flow is split between synchronous probe-time detection and async work. `beiscsi_boot_get_shandle` synchronously asks firmware whether boot targets exist and returns a valid session handle only when firmware logged in. Async boot work then calls `__beiscsi_boot_get_shandle`, possibly reopens boot sessions, fetches session info through a non-embedded command, logs out the firmware session, and asks `be_main.c` to create boot sysfs objects. `beiscsi_boot_process_compl` validates the expected tag/action, decodes the command-specific response, updates the boot action, handles retries, frees non-embedded session-info DMA memory, and reschedules boot work when progress should continue.

Connection cleanup commands split invalidation and TCP upload. `beiscsi_invalidate_cxn` posts an iSCSI driver invalidate request with cleanup type depending on whether the endpoint still has a live connection. `beiscsi_upload_cxn` posts common TCP upload with graceful or abort upload type. `beiscsi_mgmt_invalidate_icds` is used by SCSI EH to invalidate one or more firmware commands by CID/ICD table, then waits for MCC completion and frees the non-embedded buffer.

## State And Persistence Behavior

The file primarily mutates firmware state through mailbox commands. Driver-local state touched here includes `phba->interface_handle`, endpoint destination fields (`dst_addr`, `dst6_addr`, `dst_tcpport`, `ip_type`), `phba->nxt_cqid`, MCC tag state and waitqueues, async tag DMA ownership, and `phba->boot_struct`. Persistent or semi-persistent firmware state includes flash contents, initiator name, network interface configuration, default gateway, VLAN, boot target/session metadata, and active offloaded TCP/iSCSI sessions.

Non-embedded command buffers have careful ownership semantics: synchronous commands free after completion, async EQ-delay and boot session info defer or explicitly free through callbacks, and `-EBUSY` indicates the MCC completion path owns the buffer. Boot state is protected by tag/action checks rather than a separate lock; the work item and MCC callbacks communicate through `boot_struct.tag`, `boot_struct.action`, and the `BEISCSI_HBA_BOOT_WORK` bit.

## Dependencies And Integration Points

The file depends on Linux BSG, SCSI iSCSI transport headers, and local `be_mgmt.h`, `be_iscsi.h`, and `be_main.h`. It relies heavily on command helpers from `be_cmds`/`be_cmds.h` such as `alloc_mcc_wrb`, `free_mcc_wrb`, `be_wrb_hdr_prepare`, `be_cmd_hdr_prepare`, `embedded_payload`, `nonembedded_sgl`, `be_mcc_notify`, `beiscsi_mccq_compl_wait`, `__beiscsi_mcc_compl_status`, and `be_cmd_set_vlan`.

User-visible integrations are SCSI BSG vendor commands, sysfs attributes for driver/firmware/session counts/adapter family/physical port, and iSCSI boot sysfs data consumed by userspace iSCSI tooling. Hardware/firmware integration is through MCC WRBs and command opcodes in common, iSCSI, and iSCSI initiator subsystems.

## Risks And Edge Cases

Because this is the firmware management plane, return-code semantics and DMA buffer ownership are critical. Several functions return `0` both as a failure-to-post tag and as a valid nonpositive status pattern, so callers must distinguish tag-returning functions from `int` status functions. `mgmt_vendor_specific_fw_cmd` returns `-EPERM` through an unsigned return type on unsupported commands, which can be surprising to callers expecting tag-or-zero behavior.

Network configuration is stateful and multi-step; failures after clearing an IP or gateway can leave firmware configuration partially changed. `beiscsi_if_get_info` resizes its response buffer on `-EAGAIN`, which depends on firmware filling `actual_resp_len` correctly. Boot work relies on a single outstanding boot tag and retries; unexpected callbacks, tag mismatch, or missing boot-work bit are logged and ignored. CHAP names and secrets can be exposed through boot sysfs callbacks if firmware supplies them.

Generation-specific offload WRB construction must match the hardware layouts in `be_main.h`. The v0 path also writes a pad-buffer address from global-header memory; memory descriptor layout changes can break it. ICD invalidation accepts up to `BE_INVLDT_CMD_TBL_SZ` entries and waits synchronously; SCSI EH latency can be affected by firmware/MCC stalls.

## Test Signals

Validation should include firmware mailbox success and failure paths, BSG flash read/write command handling, IPv4 and IPv6 TCP connect-and-offload, static IP to DHCP and DHCP to static transitions, gateway replacement, VLAN set failures, interface-info insufficient-buffer retry, initiator-name retrieval, boot target discovery with and without configured boot sessions, boot-session reopen/get-info/logout retry behavior, connection invalidate/upload on live and half-torn-down endpoints, and ICD invalidation during SCSI abort/device reset. Runtime signals include `BG_` and `BS_` logs, MCC timeout/busy statuses, leaked coherent DMA buffers, stuck boot work bits, and incorrect interface handle caching.
