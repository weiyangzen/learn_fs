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
