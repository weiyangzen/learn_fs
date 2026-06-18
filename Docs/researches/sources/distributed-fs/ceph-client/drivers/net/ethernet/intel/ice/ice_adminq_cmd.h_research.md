# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adminq_cmd.h

## Purpose
`ice_adminq_cmd.h` is the firmware/software ABI definition for ICE Admin Queue commands, response buffers, event payloads, opcodes, and bitfields. The devlink and health files in this subset rely on it for port options, NVM activation, scheduler topology, local forwarding, CGU information, and health status events.

## Important APIs, Types, And Functions
The header defines packed context buffers for Rx, Tx, full Tx, and TxTime queue contexts. It then declares descriptor and indirect-buffer formats for command families: MAC management, switch configuration, port parameters, resource allocation, VLAN mode, VSI add/update/free, recipes and switch rules, DCB/PFC, Tx scheduler topology and rate profiles, PHY/link commands, link topology/I2C/SFF, port options, NVM read/write/activate, PF/VF mailbox, LLDP, RSS, sideband, Tx queue handling, package download/info, CGU/DPLL, driver shared parameters, LAN overflow, and health status.

Notable subset-relevant definitions include `enum ice_local_fwd_mode`, `struct ice_aqc_get_port_options`, `struct ice_aqc_get_port_options_elem`, `struct ice_aqc_set_port_option`, NVM activation flags such as `ICE_AQC_NVM_ACTIV_REQ_EMPR`, `ICE_AQC_NVM_TX_TOPO_MOD_ID` and `struct ice_aqc_nvm_tx_topo_user_sel`, CGU info structures, health status masks/codes/scopes, `struct ice_aqc_health_status_elem`, and `enum ice_adminq_opc`.

## Control Flow
Implementation files populate these structures, convert fields with little-endian helpers, and submit them through common AQ wrappers. Indirect commands carry DMA buffer addresses in `addr_high`/`addr_low`; direct commands fit in the 16-byte descriptor payload. The opcode enum selects firmware operations.

## State And Persistence
The header itself owns no state, but it defines persistent hardware and NVM state transitions: NVM writes and activation, port option persistence, Tx scheduler topology selection, LLDP persistence flags, PHY/link configuration, and package data. It also defines volatile event payloads such as link, health, LAN overflow, and LLDP events.

## Dependencies And Integration Points
It depends on `libie/adminq.h` for shared Intel admin queue definitions and Linux types/macros. It is consumed by nearly every hardware-facing ICE module, including devlink info/regions/reload, port splitting, health reporting, scheduler setup, RSS, VSI configuration, and queue programming.

## Risks And Test Signals
Risks are ABI drift against firmware, incorrect packing/alignment, endian mistakes, wrong bit masks, and variable-length flexible-array buffer sizing. Test signals include compile-time `static_assert` coverage where present, AQ command success/failure telemetry, firmware compatibility tests, devlink port split and NVM activation behavior, health event decoding, scheduler operations, RSS configuration, and broad hardware regression on multiple ICE device families.
