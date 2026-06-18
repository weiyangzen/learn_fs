# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_utils_fw2x.c

## Purpose
This file implements the Atlantic firmware 2.x operations table (`aq_fw_2x_ops`) used by the Aquantia/Marvell Atlantic NIC hardware abstraction layer. It is a firmware mailbox adapter: it discovers firmware mailbox/RPC/settings addresses, translates driver link and power policy into MPI control bits, polls firmware state bits for completion, and exposes MACsec, SMBus module EEPROM, PTP, EEE, flow-control, WoL, statistics, and temperature hooks through `struct aq_fw_ops`.

## Important APIs, types, and functions
The exported integration point is `const struct aq_fw_ops aq_fw_2x_ops`. Key methods include `aq_fw2x_init`, `aq_fw2x_deinit`, `aq_fw2x_set_link_speed`, `aq_fw2x_set_state`, `aq_fw2x_update_link_status`, `aq_fw2x_update_stats`, `aq_fw2x_get_phy_temp`, `aq_fw2x_set_power`, `aq_fw2x_set_eee_rate`, `aq_fw2x_get_eee_rate`, `aq_fw2x_set_flow_control`, `aq_fw2x_get_flow_control`, `aq_fw2x_send_fw_request`, `aq_fw2x_set_phyloopback`, `aq_fw2x_set_downshift`, `aq_fw2x_set_media_detect`, `aq_fw2x_send_macsec_req`, and `aq_fw2x_read_module_eeprom`. `fw2x_msg_wol` and `fw2x_msg_wol_pattern` describe an older WoL RPC payload; the actual magic-packet path uses `hw_atl_utils_fw_rpc`.

## Control flow
Initialization polls `HW_ATL_FW2X_MPI_MBOX_ADDR` and `HW_ATL_FW2X_MPI_RPC_ADDR`, then reads the settings address from the mailbox. Link setup writes a firmware rate mask to `MPI_CONTROL`, then `MPI_INIT` updates `MPI_CONTROL2` with EEE and pause bits. Several commands follow a common pattern: write firmware-facing memory, toggle a capability/control bit, and poll `MPI_STATE` or `MPI_STATE2` until firmware mirrors the transition. Stats and temperature are requested by toggling `CAPS_HI_STATISTICS` or `CTRL_TEMPERATURE`; MACsec and SMBus requests toggle low capability bits in `MPI_CONTROL`.

## State and persistence
State is persisted in hardware registers and firmware-owned mailbox/RPC/settings memory, not in kernel files. The driver caches discovered mailbox addresses in `aq_hw_s` (`mbox_addr`, `rpc_addr`, `settings_addr`) and updates `aq_link_status` plus current stats. WoL programming writes firmware sleep proxy information so behavior persists while the host enters low-power states.

## Dependencies and integration points
The file depends on Atlantic common helpers (`aq_hw_read_reg`, `aq_hw_write_reg`, firmware dword download/write helpers), NIC configuration (`aq_nic_cfg_s`), and Linux polling macros. MACsec support flows into the `macsec` API via the firmware `send_macsec_req` operation, while module EEPROM reads are exposed to ethtool/SFP paths through `read_module_eeprom`. PTP enable/adjust uses firmware 3.x extension registers even though it is attached to the 2.x ops table.

## Risks
Most operations rely on magic register offsets and bit toggles; mismatched firmware versions can produce silent `-EIO`, `-ETIME`, or `-EOPNOTSUPP` paths. `aq_fw2x_get_mac_permanent` returns a zero MAC if the efuse pointer is absent, leaving callers to validate. SMBus trailing-byte reads cast response memory to dwords and require careful length handling. `aq_fw2x_set_wol` ignores the link-drop polling return for `WAKE_PHY`, so firmware failure there can be partially hidden.

## Test signals
Useful signals are successful firmware init polling, link speed changes reflected in `aq_link_status.mbps`, ethtool EEE and pause configuration round-trips, MACsec request success only when `CAPS_LO_MACSEC` is set, SFP EEPROM reads through SMBus-capable firmware, WoL wake tests, and timeout/error logs from `readx_poll_timeout_atomic`.
