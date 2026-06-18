# Research: subset-b-004611

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_init.c

## Purpose
This file implements 83xx-family adapter initialization, inter-driver communication (IDC) state handling, firmware reset/restart, reset-template execution, vNIC/default operating-mode selection, firmware-image loading, POST execution, and PCI AER recovery hooks. It is the main orchestration layer that brings a 83xx device from firmware/flash state into a running NIC function and keeps all PCI functions coordinated during reset and failure recovery.

## Important APIs, Types, And Functions
- Reset-template structures: `struct qlc_83xx_reset_hdr`, `struct qlc_83xx_entry_hdr`, `struct qlc_83xx_poll`, `struct qlc_83xx_rmw`, `struct qlc_83xx_entry`, and `struct qlc_83xx_quad_entry` describe the flash-provided command stream used to stop, initialize, and start hardware.
- IDC exported entry points: `qlcnic_83xx_idc_init()`, `qlcnic_83xx_idc_exit()`, `qlcnic_83xx_idc_poll_dev_state()`, `qlcnic_83xx_idc_request_reset()`, `qlcnic_83xx_idc_ready_state_entry()`, `qlcnic_83xx_idc_vnic_pf_entry()`, and `qlcnic_83xx_idc_reattach_driver()`.
- Main adapter init: `qlcnic_83xx_init()` initializes mailbox work, SR-IOV/VF paths, flash descriptors, IDC, interrupts, DCB, NIC mode, and mode-specific driver setup.
- Firmware/restart helpers: `qlcnic_83xx_restart_hw()`, `qlcnic_83xx_copy_bootloader()`, `qlcnic_83xx_copy_fw_file()`, `qlcnic_83xx_load_fw_image_from_host()`, and `qlcnic_83xx_run_post()`.
- Template executor: `qlcnic_83xx_exec_template_cmd()` dispatches opcodes such as write-list, read/write-list, poll-list, poll-write-list, read-modify-write, sequence pause/end, template end, and poll-read-list.
- Opmode and rings: `qlcnic_83xx_get_nic_configuration()`, `qlcnic_83xx_configure_opmode()`, `qlcnic_83xx_init_default_driver()`, `qlcnic_83xx_config_buff_descriptors()`, and `qlcnic_83xx_init_rings()`.
- AER hooks: `qlcnic_83xx_aer_stop_poll_work()`, `qlcnic_83xx_aer_reset()`, and `qlcnic_83xx_aer_start_poll_work()`.

## Control Flow
`qlcnic_83xx_init()` sets MSI-X preference, POST mode from `qlcnic_load_fw_file`, initializes default ring counts, creates mailbox work, and diverts SR-IOV VFs into `qlcnic_sriov_vf_init()`. For PF/default paths it reads flash metadata, verifies command PEG/heartbeat, allocates firmware metadata, initializes IDC, sets up interrupts/mailbox interrupts, clears stale function resources, enables DCB, initializes the NIC, chooses default/vNIC mode, calls `adapter->nic_ops->init_driver`, and starts periodic IDC polling.

IDC state is driven by `qlcnic_83xx_idc_poll_dev_state()`, which reads `QLC_83XX_IDC_DEV_STATE`, validates legal transitions, dispatches to handlers for READY, NEED_RESET, NEED_QUIESCENT, FAILED, INIT, and QUIESCENT, updates previous state, runs periodic filter pruning, and reschedules while `QLC_83XX_MODULE_LOADED` is set. READY checks temperature, firmware heartbeat, graceful reset requests, firmware dump requests, TX soft reset requests, and quiesce requests. NEED_RESET detaches the driver, disables mailbox readiness, optionally disables vNIC mode, waits for diagnostic completion, ACKs reset, waits for peer function ACKs, and transitions to INIT. INIT lets the reset owner restart hardware. FAILED records errors and may stop hardware/dump firmware if reset recovery is disabled.

Hardware restart is reset-template based. `qlcnic_83xx_get_reset_instruction_template()` reads a template header and body from flash, validates checksum, and records stop/start/init offsets. `qlcnic_83xx_restart_hw()` executes stop/init/start phases, optionally dumps firmware, copies bootloader to memory, optionally runs POST firmware, chooses host or flash firmware image, starts hardware, and validates command PEG plus heartbeat.

## State And Persistence Behavior
Persistent adapter state lives in `adapter`, `adapter->ahw`, hardware CRB/shared registers, firmware image-valid registers, and flash-provided reset templates. IDC uses hardware registers including driver presence, ACK, audit, major/minor version, control, and device-state registers so multiple PCI functions coordinate through device-visible state rather than process-local state. The reset template is cached in `ahw->reset.buff` and reused unless the firmware version increases. Work scheduling uses `adapter->fw_work` and `adapter->idc_aen_work`; module-loaded and resetting bits gate polling and concurrent reset operations. Firmware images are transiently requested from userspace firmware storage and released after copying.

## Dependencies And Integration Points
This file depends heavily on `qlcnic.h`, `qlcnic_hw.h`, `qlcnic_sriov.h`, mailbox helpers, flash access, indirect register access, firmware dump/minidump helpers, interrupt setup, DCB attach/info, SR-IOV PF/VF reinit/reset helpers, netdev open/close paths, and vNIC configuration implemented in `qlcnic_83xx_vnic.c`. It exports reset and init hooks consumed by the main qlcnic adapter probe/remove, watchdog, AER, and ethtool dump/reset request paths.

## Risks And Edge Cases
- IDC correctness depends on shared-register locking through `qlcnic_83xx_lock_driver()`; skipped or failed locking can strand peer functions in NEED_RESET/INIT states.
- Reset ACK timeout forcibly clears non-ACKing functions from presence, which allows recovery but can hide a stuck function.
- The reset-template interpreter trusts flash-provided sizes/offsets after checksum validation; malformed templates can drive unexpected register operations.
- `qlcnic_83xx_reset_template_checksum()` has inverted-looking success logic (`~sum` returns success), so checksum behavior deserves focused review against hardware format.
- Some quiesce paths are logged as `TBD`, making graceful quiesce less complete than reset handling.
- Firmware restart performs blocking sleeps, DMA/MS memory writes, and firmware requests in recovery paths; callers must be in sleepable context.
- AER reset relies on reset-owner election and `idc->state_entry`; incorrect opmode/state-entry assignment can leave devices detached.

## Test Signals
Useful validation signals include probe success through `qlcnic_83xx_init()`, IDC state transition logs, successful command PEG/heartbeat checks, firmware dump/reset requests through ethtool, POST pass/fail signatures, vNIC mode enable/disable state, DCB info refresh after reattach, AER reset recovery, and absence of stuck `__QLCNIC_RESETTING` or `QLC_83XX_MODULE_LOADED` states after remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_vnic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_vnic.c

## Purpose
This file implements 83xx vNIC/NPAR operating-mode setup. It decides whether a PCI function is management, privileged, or non-privileged, configures function opmode registers, initializes the correct vNIC role, manages vNIC operational state, and records eSwitch enablement per physical port.

## Important APIs, Types, And Functions
- `qlcnic_83xx_config_vnic_opmode()` reads `QLC_83XX_DRV_OP_MODE`, derives function privilege, assigns `ahw->op_mode`, sets IDC state-entry callbacks, and assigns `adapter->nic_ops->init_driver`.
- `qlcnic_83xx_init_mgmt_vnic()` initializes the management function, reads PCI/NIC partition information, sets opmode, default offload settings, port info, descriptor limits, MSI-X support, and enables vNIC mode.
- `qlcnic_83xx_init_privileged_vnic()` and `qlcnic_83xx_init_non_privileged_vnic()` initialize privileged and VF-like non-privileged vNIC roles.
- `qlcnic_83xx_set_vnic_opmode()` marks the current function as management in the driver opmode register.
- `qlcnic_83xx_disable_vnic_mode()` and internal `qlcnic_83xx_enable_vnic_mode()` write `QLC_83XX_VNIC_STATE`.
- `qlcnic_83xx_check_vnic_state()` waits for management function to make vNIC mode operational.
- `qlcnic_83xx_set_port_eswitch_status()` queries NIC info and marks an eSwitch as enabled for a port.

## Control Flow
`qlcnic_83xx_configure_opmode()` in the init file calls `qlcnic_83xx_config_vnic_opmode()` when NIC capabilities indicate eSwitch/vNIC mode. This file first records the PCI function number, reads opmode, maps default opmode to management, and selects the role-specific init routine. Management functions perform partition discovery and opmode programming, reset NPAR config on reinit, fetch port info, configure descriptors, and write vNIC state operational. Privileged functions wait for management-enabled vNIC mode through `qlcnic_83xx_idc_vnic_pf_entry()` in the init file. Non-privileged functions refresh firmware version, apply eSwitch port config, get port info, and use vNIC descriptor limits.

## State And Persistence Behavior
The primary persistent state is hardware-backed: `QLC_83XX_DRV_OP_MODE` encodes per-function privilege, and `QLC_83XX_VNIC_STATE` indicates NPAR operational state. The adapter mirrors this in `ahw->op_mode`, `ahw->idc.vnic_state`, `ahw->idc.vnic_wait_limit`, flags such as `QLCNIC_ADAPTER_INITIALIZED` and `QLCNIC_ESWITCH_ENABLED`, descriptor counts, ring limits, MSI-X support, and MAC learning booleans.

## Dependencies And Integration Points
This file depends on IDC callbacks from `qlcnic_83xx_init.c`, PCI/NIC information helpers from context/mailbox code, port-info and default-offload helpers, eSwitch configuration routines, global `qlcnic_use_msi_x`, and adapter templates in `adapter->nic_ops`. It is the vNIC-specific branch of 83xx initialization and is also used during reset recovery when vNIC mode must be disabled or re-enabled.

## Risks And Edge Cases
- Management-function initialization is the only path that enables vNIC mode; privileged functions can time out if management does not finish.
- `qlcnic_83xx_set_vnic_opmode()` always programs the current function as management when called by management init, so misidentifying privilege can affect all functions.
- Non-privileged initialization assumes eSwitch port configuration succeeds before port info/ring setup.
- `qlcnic_83xx_check_vnic_state()` sleeps in one-second increments and consumes `vnic_wait_limit`; callers need to reset the wait limit before reuse.
- eSwitch enablement is based on firmware capabilities returned by `qlcnic_get_nic_info`; stale/failed mailbox responses disable the path.

## Test Signals
Test signals include logs identifying Management/Privileged/Virtual function HAL version, successful vNIC operational state transition, timeout logs from `qlcnic_83xx_check_vnic_state()`, descriptor counts appropriate to 1G/10G ports, `QLCNIC_ESWITCH_ENABLED` flag behavior, and correct RX MAC learning behavior when `drv_mac_learn` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_vnic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ctx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ctx.c

## Purpose
This file implements 82xx-style mailbox command allocation/issue, firmware RX/TX context creation/destruction, hardware DMA ring allocation/free, interrupt configuration, NIC/PCI/eSwitch information mailbox APIs, MAC address retrieval, MAC/eSwitch statistics, and eSwitch port configuration. It is the firmware-control and resource-context layer shared by upper qlcnic init, open, reset, ethtool, and management paths.

## Important APIs, Types, And Functions
- `qlcnic_mbx_tbl[]` maps firmware command IDs to request/response argument counts used by `qlcnic_82xx_alloc_mbx_args()`.
- `qlcnic_82xx_issue_cmd()` serializes command register access with `qlcnic_api_lock()`, writes command signature and arguments, polls response, maps firmware response codes, reads response args, and unlocks.
- Context lifecycle: `qlcnic_82xx_fw_cmd_create_rx_ctx()`, `qlcnic_82xx_fw_cmd_del_rx_ctx()`, `qlcnic_82xx_fw_cmd_create_tx_ctx()`, `qlcnic_82xx_fw_cmd_del_tx_ctx()`, `qlcnic_fw_create_ctx()`, and `qlcnic_fw_destroy_ctx()`.
- DMA resource lifecycle: `qlcnic_alloc_hw_resources()` and `qlcnic_free_hw_resources()` allocate/free TX command rings, TX hardware consumer memory, RDS rings, and SDS rings.
- Device configuration/query: `qlcnic_fw_cmd_set_drv_version()`, `qlcnic_fw_cmd_set_mtu()`, `qlcnic_fw_cmd_set_port()`, `qlcnic_82xx_config_intrpt()`, `qlcnic_82xx_get_mac_address()`, `qlcnic_82xx_get_nic_info()`, `qlcnic_82xx_set_nic_info()`, `qlcnic_82xx_get_pci_info()`.
- Management/eSwitch APIs: `qlcnic_config_port_mirroring()`, `qlcnic_get_port_stats()`, `qlcnic_get_mac_stats()`, `qlcnic_get_eswitch_stats()`, `qlcnic_clear_esw_stats()`, `qlcnic_config_switch_port()`, and `qlcnic_get_eswitch_port_config()`.

## Control Flow
Mailbox callers allocate request/response arrays with `qlcnic_alloc_mbx_args()`, populate command-specific arguments, call `qlcnic_issue_cmd()`, interpret response arguments, and free args. Context creation first allocates DMA-coherent host request and card response structures, fills ring metadata and capabilities, sends firmware create commands, then maps firmware-returned CRB offsets into per-ring producer/consumer/interrupt-mask pointers. `qlcnic_fw_create_ctx()` optionally performs FLR, configures MSI-X/multi-queue interrupts for 83xx or 82xx, creates RX context, creates all TX contexts, and sets `__QLCNIC_FW_ATTACHED`. Failures unwind created contexts and interrupt configuration. `qlcnic_fw_destroy_ctx()` reverses this and delays briefly for DMA queue drain.

Management calls generally allocate a DMA buffer for little-endian firmware structures, issue a mailbox command with physical address and size, translate endianness into host structs, and free DMA memory. eSwitch configuration first validates management-function privilege and function IDs, reads current port config, edits bitfields, and writes back through firmware.

## State And Persistence Behavior
This file persists firmware context IDs, host context states, DMA physical addresses, CRB pointers, ring producers/consumers, interrupt table IDs/sources/enabled flags, total NIC/PCI function counts, NIC partition data, eSwitch configuration, and statistics snapshots. DMA memory is coherent and must remain valid while firmware contexts are active. Firmware mailbox state is transient in request/response arrays but serialized through CRB locks. `__QLCNIC_FW_ATTACHED` is the high-level state bit that prevents duplicate destroy operations.

## Dependencies And Integration Points
The code integrates with PCI DMA APIs, netdev state, qlcnic ring structs, firmware command definitions, mailbox locking, endian conversion helpers, interrupt setup for 82xx/83xx, SR-IOV/vNIC management, ethtool statistics, and NPAR/eSwitch admin operations. Many function names are 82xx-prefixed but are reachable through adapter operation tables or compatibility paths.

## Risks And Edge Cases
- `qlcnic_82xx_alloc_mbx_args()` returns success even if the command type is not found, leaving `req.arg` unset; callers rely on only supported commands being requested.
- Context creation has multiple DMA allocations and firmware calls; unwind correctness is critical to avoid leaked coherent memory or live firmware contexts without host state.
- `qlcnic_fw_create_ctx()` deletes the RX context inside TX-context failure and then deletes previously created TX contexts; error ordering matters if firmware partially creates resources.
- Management-only operations return `-EIO` for non-management functions; callers must not expose privileged operations to ordinary VFs/functions.
- Statistics aggregation uses sentinel values such as `QLCNIC_STATS_NOT_AVAIL`; consumers must handle unavailable counters.
- eSwitch bitfield packing is dense, and incorrect op_mode/op_type or VLAN fields can alter anti-spoof/offload/promisc behavior.

## Test Signals
Important signals include mailbox timeout/failure logs, successful RX/TX context creation logs with IDs and states, `__QLCNIC_FW_ATTACHED` transitions, interrupt add/delete logs, ring DMA allocation/unwind under fault injection, management function validation errors, accurate total function counts from PCI info, ethtool MAC/eSwitch stats, and VLAN/port-mirroring config reflected in firmware responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ctx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.c

## Purpose
This file implements Data Center Bridging (DCB/DCBX) support for qlcnic adapters when `CONFIG_QLCNIC_DCB` is enabled. It registers adapter-local DCB state, selects 82xx or 83xx DCB operations, queries firmware DCB capabilities and CEE parameters, maps firmware mailbox bitfields into kernel DCBNL-visible structures, refreshes state on asynchronous events, and exposes read-only/LLD-managed DCB operations to the networking stack.

## Important APIs, Types, And Functions
- DCB operation tables: `qlcnic_82xx_dcb_ops` and `qlcnic_83xx_dcb_ops` implement the function-pointer interface declared in `qlcnic_dcb.h`.
- Registration/lifecycle: `qlcnic_register_dcb()`, `__qlcnic_dcb_attach()`, `__qlcnic_dcb_free()`, `__qlcnic_init_dcbnl_ops()`, and `__qlcnic_dcb_get_info()`.
- Firmware query paths: `__qlcnic_dcb_query_hw_capability()`, `__qlcnic_dcb_get_capability()`, `qlcnic_82xx_dcb_get_hw_capability()`, `qlcnic_83xx_dcb_get_hw_capability()`, `qlcnic_82xx_dcb_query_cee_param()`, `qlcnic_83xx_dcb_query_cee_param()`, and corresponding `get_cee_cfg()` functions.
- Mapping helpers: `qlcnic_dcb_fill_cee_tc_params()`, `qlcnic_dcb_fill_cee_pg_params()`, `qlcnic_dcb_fill_cee_app_params()`, `qlcnic_dcb_map_cee_params()`, and `qlcnic_dcb_data_cee_param_map()`.
- AEN refresh: `qlcnic_dcb_aen_work()`, `qlcnic_82xx_dcb_aen_handler()`, and `qlcnic_83xx_dcb_aen_handler()`.
- DCBNL operations: `qlcnic_dcb_get_state()`, `getpgtccfgtx`, `getpgbwgcfgtx`, `getpfccfg`, `getcap`, `getnumtcs`, `getapp`, `getpfcstate`, `getdcbx`, `getfeatcfg`, peer app table/info, and CEE peer PG/PFC getters.

## Control Flow
`qlcnic_register_dcb()` skips SR-IOV VFs, allocates `struct qlcnic_dcb`, attaches it to the adapter, and assigns ops based on adapter generation. During 83xx initialization, `qlcnic_dcb_enable()` calls `__qlcnic_dcb_attach()` to initialize delayed work, create a single-thread workqueue, and allocate config/parameter buffers. `qlcnic_dcb_get_info()` first queries capabilities; if firmware reports DCBX plus TSA/ETS support, `QLCNIC_DCB_STATE` is set. It then queries local, operational, and peer CEE parameters and maps them into `dcb->cfg`.

82xx parameter queries use a DMA response buffer containing little-endian `struct qlcnic_82xx_dcb_param_mbx_le`; 83xx queries use mailbox response arguments directly with a firmware-version bit in the command. Mapping fills TC, priority group, PFC, and application priority state. Operational app entries are registered with `dcb_setapp()`, and `dcbnl_cee_notify()` notifies userspace. AEN handlers set a mode bit, optionally update DCB enabled state for 83xx based on event data, queue work, and the worker refreshes CEE config before clearing the mode bit.

## State And Persistence Behavior
Persistent state is held in `adapter->dcb`, `dcb->state`, `dcb->cfg`, and `dcb->param`. `QLCNIC_DCB_STATE` means DCB is usable and controls whether `netdev->dcbnl_ops` is installed. `QLCNIC_DCB_AEN_MODE` serializes asynchronous refresh handling and is waited on during free. The firmware CEE data is cached in both raw mailbox form (`struct qlcnic_dcb_mbx_params`) and mapped kernel-facing form (`struct qlcnic_dcb_cfg`). Application priorities may also be persisted in the kernel DCB app table via `dcb_setapp()`.

## Dependencies And Integration Points
The file depends on qlcnic mailbox command allocation/issue, adapter generation detection, netdev DCBNL APIs, workqueues, delayed work, firmware DCB command IDs, CEE structures, and device AEN delivery. `qlcnic_dcb.h` provides no-op wrappers when the config option is disabled, so callers in init/reset code can remain unconditional.

## Risks And Edge Cases
- DCB is LLD-managed and mostly read-only; attempts to infer writable behavior from DCBNL ops would be incorrect.
- The 83xx mailbox response parsing uses fixed response indices and copies a fixed 16-DWORD block for each parameter type; command metadata and firmware ABI must match exactly.
- `qlcnic_dcb_prio_count()` returns the first set priority bit, not a population count, so app priority mapping assumes one priority bit is meaningful.
- Free waits while `QLCNIC_DCB_AEN_MODE` is set; if queued work never runs or hangs, teardown can wait repeatedly.
- `qlcnic_dcb_cee_peer_get_pg()` indexes `peer->tc_cfg[i]` while iterating PG IDs; unusual PG/TC mappings could produce incomplete peer PG reporting.
- DCBNL ops access `adapter->dcb` and nested config without broad locking beyond AEN mode, so reset/free ordering is important.

## Test Signals
Useful signals include DCB registration skipped for SR-IOV VFs, workqueue/config allocation failures, firmware DCB capability errors, `QLCNIC_DCB_STATE` set/cleared behavior, DCBNL output for PG/PFC/app/peer data, `dcbnl_cee_notify()` after AEN refresh, and teardown under active AEN refresh without use-after-free or stuck waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.h

## Purpose
This header defines the public DCB integration surface for qlcnic. It hides optional `CONFIG_QLCNIC_DCB` support behind wrappers, declares the DCB object and operation table, and provides safe inline dispatch helpers used by the rest of the driver.

## Important APIs, Types, And Functions
- `QLCNIC_DCB_STATE` and `QLCNIC_DCB_AEN_MODE` are state-bit indices used by the DCB implementation.
- `qlcnic_register_dcb()` is declared when DCB is enabled and compiled as a no-op returning success when disabled.
- `struct qlcnic_dcb_ops` defines callbacks for hardware capability queries, CEE parameter queries/config, DCBNL operation initialization, AEN handling, attach, free, and info refresh.
- `struct qlcnic_dcb` stores raw parameters, adapter backpointer, delayed AEN work, workqueue, ops table, mapped config, and state bits.
- Inline wrappers include `qlcnic_dcb_get_hw_capability()`, `qlcnic_dcb_free()`, `qlcnic_dcb_attach()`, `qlcnic_dcb_query_hw_capability()`, `qlcnic_dcb_get_info()`, `qlcnic_dcb_query_cee_param()`, `qlcnic_dcb_get_cee_cfg()`, `qlcnic_dcb_aen_handler()`, `qlcnic_dcb_init_dcbnl_ops()`, and `qlcnic_dcb_enable()`.

## Control Flow
Callers allocate/register DCB through `qlcnic_register_dcb()`, enable it through `qlcnic_dcb_enable()`, refresh firmware-derived state with `qlcnic_dcb_get_info()`, expose DCBNL ops through `qlcnic_dcb_init_dcbnl_ops()`, and handle adapter events with `qlcnic_dcb_aen_handler()`. Each wrapper checks both object and callback presence before dispatching.

## State And Persistence Behavior
The header itself stores no state, but it standardizes state access through `struct qlcnic_dcb`. The wrappers return `-EOPNOTSUPP` when a DCB object or callback is unavailable, except `qlcnic_dcb_enable()` which treats a missing DCB object as success so non-DCB or disabled-DCB builds do not fail adapter initialization.

## Dependencies And Integration Points
This header is included by core qlcnic init/reset paths and the DCB implementation. It depends on the driver adapter type and Linux error codes. Its compile-time no-op behavior is the key integration point that lets callers use DCB hooks unconditionally regardless of kernel config.

## Risks And Edge Cases
- Most wrappers dereference `dcb->ops` without checking that `ops` itself is non-NULL when `dcb` exists; registration must assign ops before wrappers are used.
- Missing callbacks map to `-EOPNOTSUPP`, which callers must either tolerate or treat as a real failure depending on context.
- `qlcnic_dcb_enable()` returning success for NULL DCB is intentional but can mask registration failures if callers expect DCB to be mandatory.

## Test Signals
Compile coverage should include both `CONFIG_QLCNIC_DCB=y` and disabled builds. Runtime signals include successful no-op adapter init when DCB is disabled, valid wrapper return values for missing/unsupported callbacks, and correct dispatch to 82xx/83xx ops after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ethtool.c

## Purpose
This file implements the qlcnic `ethtool_ops` tables for PF/default, SR-IOV VF, and failed-adapter modes. It exposes driver/firmware identity, link settings, registers, EEPROM, ring parameters, channels, pause settings, diagnostics, strings/statistics, LED identification, Wake-on-LAN, interrupt coalescing, message level, and firmware dump/reset controls.

## Important APIs, Types, And Functions
- Statistics definitions: `struct qlcnic_stats`, `qlcnic_gstrings_stats`, queue stat strings, 83xx TX/MAC/RX stat strings, eSwitch stat strings, and diagnostic test strings.
- Capability/length helpers: `qlcnic_dev_statistics_len()`, `qlcnic_get_regs_len()`, `qlcnic_get_eeprom_len()`, and `qlcnic_get_sset_count()`.
- Link and port configuration: `qlcnic_get_link_ksettings()`, `qlcnic_82xx_get_link_ksettings()`, `qlcnic_set_link_ksettings()`, and `qlcnic_set_port_config()`.
- Register/EEPROM/ring/channel/pause paths: `qlcnic_get_regs()`, `qlcnic_get_eeprom()`, `qlcnic_get_ringparam()`, `qlcnic_set_ringparam()`, `qlcnic_get_channels()`, `qlcnic_set_channels()`, `qlcnic_get_pauseparam()`, and `qlcnic_set_pauseparam()`.
- Diagnostics: `qlcnic_reg_test()`, `qlcnic_eeprom_test()`, `qlcnic_irq_test()`, `qlcnic_loopback_test()`, `qlcnic_do_lb_test()`, and `qlcnic_diag_test()`.
- Stats: `qlcnic_get_strings()`, `qlcnic_update_stats()`, `qlcnic_get_ethtool_stats()`, `qlcnic_fill_stats()`, and `qlcnic_fill_tx_queue_stats()`.
- Firmware dump/reset: `qlcnic_enable_fw_dump_state()`, `qlcnic_disable_fw_dump_state()`, `qlcnic_check_fw_dump_state()`, `qlcnic_get_dump_flag()`, `qlcnic_get_dump_data()`, `qlcnic_set_dump_mask()`, and `qlcnic_set_dump()`.
- Exported operation tables: `qlcnic_ethtool_ops`, `qlcnic_sriov_vf_ethtool_ops`, and `qlcnic_ethtool_failed_ops`.

## Control Flow
Ethtool calls enter through one of the exported ops tables. Most operations branch by adapter generation: 83xx-specific helpers handle 83xx register dumps, link settings, pause, interrupt test, loopback, flash test, LED, and statistics, while this file directly implements 82xx/default behavior. Ring-size changes validate descriptor counts, update adapter fields, and call `qlcnic_reset_context()`. Channel changes require MSI-X, validate RX/TX queue counts, update RSS/TSS requested counts, set `QLCNIC_TSS_RSS`, and rebuild rings. Offline diagnostics run register/link checks for all requests and IRQ/loopback/EEPROM checks only for `ETH_TEST_FL_OFFLINE`.

Statistics collection first emits per-TX-ring software counters, then adapter software counters, then generation-specific firmware stats. 83xx stats are filled only when link is up. 82xx MAC stats use mailbox queries, and eSwitch stats are appended when eSwitch is enabled.

Firmware dump controls use ethtool dump flags. Force dump and force reset call `qlcnic_dev_request_reset()`. Enable/disable toggles either the local `fw_dump->enable` flag or, for 84xx, bits in `QLC_83XX_IDC_CTRL` under driver lock. Dump retrieval copies template header as little-endian words, appends captured data, frees the dump buffer, and clears the available flag.

## State And Persistence Behavior
This file reads and mutates adapter software stats, ring counts, RSS/TSS counts, link settings, pause bits in registers, diagnostic/reset bits, LED state, WOL register bits, coalescing settings, message level, and firmware dump state. Some changes persist only in adapter memory until reset/reopen, while others are written to firmware or CRB registers. Dump retrieval is destructive: it frees `fw_dump->data` and clears `fw_dump->clr` after successful extraction.

## Dependencies And Integration Points
It integrates with Linux ethtool, netdev open/stop, PCI identity, qlcnic mailbox/context reset, hardware register macros from `qlcnic_hdr.h`, 83xx-specific ethtool helpers, firmware dump/minidump infrastructure, diagnostics allocation/free, loopback packet TX/RX paths, DCB/eSwitch stats, and qlcnic reset request handling.

## Risks And Edge Cases
- Several ethtool operations can trigger context reset, netdev stop/open, firmware reset, or firmware dump; callers must expect disruptive side effects.
- `qlcnic_get_eeprom()` returns success without data for 83xx, while `qlcnic_eeprom_test()` delegates to 83xx flash test; this asymmetry can surprise consumers.
- Offline diagnostics manipulate `__QLCNIC_RESETTING`, ring counts, diagnostic resources, and loopback mode; unwind paths must restore counts and clear reset state.
- Stats string counts must stay exactly aligned with data fill order; adding/removing stats in one array requires updating count and fill paths together.
- `qlcnic_get_ethtool_stats()` skips 83xx firmware stats when link is down, leaving zeros for those slots.
- Firmware dump mask changes require dump support and enabled state; retrieving a dump clears the stored data, so repeated reads differ.

## Test Signals
Test with `ethtool -i`, `-k/-S/-g/-G/-l/-L/-a/-A`, register dumps, link setting changes, offline and online self-tests, LED identify, coalesce get/set, WOL get/set on supported 82xx hardware, firmware dump enable/disable/force/read, SR-IOV VF ethtool capability restrictions, and failed-adapter ops availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hdr.h

## Purpose
This header defines low-level register maps, bit constants, address windows, device states, firmware error helpers, interrupt register mappings, NIU flow-control helpers, mailbox CRB addresses, memory address ranges, and small hardware mapping structs for qlcnic 82xx/P3P-style hardware. It is a foundational hardware ABI header used by init, ethtool, context, interrupt, flash, and link-management code.

## Important APIs, Types, And Definitions
- Hub/agent enumerations define CRB hub addresses and PX map indices for PH/PS/MN/MS/PEG/SRE/NIU/QM/SQ/CAS/I2C/ROMUSB and related blocks.
- `BIT_0` through `BIT_31`, `LSB/MSB/LSW/MSW/LSD/MSD`, and many register-address macros support compact hardware bitfield programming.
- CRB windows: `QLCNIC_PCI_CRB_WINDOW*`, `QLCNIC_CRB_*`, PEG, DDR/QDR/OCM ranges, ROMUSB, CAM, NIU, timer, I2Q, and PCI host/MD windows.
- Mailbox command register macros: `QLCNIC_CDRP_ARG()`, `QLCNIC_CDRP_CRB_OFFSET`, and `QLCNIC_SIGN_CRB_OFFSET`.
- Link/port helpers: `XG_LINK_STATE_P3P()`, `P3P_LINK_SPEED_REG()`, `P3P_LINK_SPEED_VAL()`, `QLCNIC_PORT_MODE_*`, and NIU pause/flow-control bit setters/getters.
- Device state and function mode enums include cold/initializing/ready/need-reset/failed/quiescent states and management/privileged/non-privileged/SR-IOV modes.
- Firmware error macros parse fatal/error code fields and define fan failure.
- Interrupt definitions include legacy target status/mask registers for functions 0-7 and `QLCNIC_LEGACY_INTR_CONFIG`.
- Structs `qlcnic_legacy_intr_set`, `crb_128M_2M_sub_block_map`, and `crb_128M_2M_block_map` describe interrupt register sets and CRB address translation maps.

## Control Flow
The header has no executable control flow, but its macros determine how source files compute hardware addresses and manipulate state. Context code writes mailbox arguments through `QLCNIC_CDRP_ARG()`. Ethtool reads link, pause, WOL, and diagnostic registers defined here. Init and reset code compares device states, heartbeat timing constants, and firmware error codes. Interrupt setup uses the legacy interrupt config initializer.

## State And Persistence Behavior
Definitions in this header map directly to persistent hardware state: CRB registers, CAM RAM, ROM/flash windows, shared device-state registers, WOL config, link speed/state, pause masks, firmware heartbeat/PEG halt registers, mailbox registers, and interrupt masks/status. Writes through these macros can persist in device registers across driver operations and sometimes across function resets depending on hardware block.

## Dependencies And Integration Points
The header includes Linux kernel types and `qlcnic_hw.h`. It is consumed by most qlcnic low-level C files, especially ethtool, context/mailbox, hardware register access, reset, link, and flash code. It bridges driver logic to firmware/hardware ABI constants; changing values without matching hardware documentation would affect many paths.

## Risks And Edge Cases
- Macros with side effects such as `qlcnic_gb_rx_flowctl(config_word)` modify their argument expression; callers must pass mutable lvalues.
- Many numeric constants are hardware ABI values with no type safety; a wrong register base or bit shift can silently access the wrong device block.
- Duplicated comments around NIU XG pause control and dense hub-agent mapping make maintenance error-prone.
- Legacy BIT macros may conflict conceptually with kernel `BIT()` usage, but local code expects these exact constants.
- Device-state constants here are distinct from 83xx IDC state constants in other headers; mixing state domains would cause invalid transitions.

## Test Signals
Validation signals include successful mailbox commands using CDRP offsets, correct ethtool register/link/pause/WOL behavior, interrupt delivery for legacy/MSI-X paths, flash/ROMUSB access, heartbeat and PEG halt diagnostics, and regression tests or hardware smoke tests after any register macro changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_hdr.h -->
