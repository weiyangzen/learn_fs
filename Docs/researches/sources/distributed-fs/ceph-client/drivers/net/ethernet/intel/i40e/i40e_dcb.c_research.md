# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.c

## Purpose

`i40e_dcb.c` implements the core Data Center Bridging path for the Intel i40e driver. It translates LLDP/DCBX MIB data into `struct i40e_dcbx_config`, serializes local DCB configuration back into IEEE LLDP TLVs, initializes DCB state from firmware/NVM, and directly programs receive-side DCB/PFC packet-buffer registers used by software-controlled DCB.

## Important APIs, Types, And Functions

- `i40e_get_dcbx_status()` reads `I40E_PRTDCB_GENS` and extracts firmware DCBX engine status.
- `i40e_lldp_to_dcb_config()` walks an LLDPDU after the Ethernet header, dispatching organization TLVs to IEEE or CEE parsers until END TLV or `I40E_LLDPDU_SIZE`.
- IEEE parsers populate ETS, PFC, and application priority tables; CEE parsers convert PG, PFC, and APP feature TLVs into the same internal config.
- `i40e_aq_get_dcb_config()`, `i40e_get_dcb_config()`, and `i40e_init_dcb()` are the firmware-facing retrieval and initialization entry points.
- `i40e_set_dcb_config()` and `i40e_dcb_config_to_lldp()` serialize local config into IEEE TLVs and submit it through `i40e_aq_set_lldp_mib()`.
- Hardware programming helpers configure Rx FIFO arbitration, command monitor thresholds, PFC registers, TC count, Rx ETS bandwidth, UP-to-TC mapping, packet-buffer sizing, and packet-buffer watermarks.

## Control Flow

Initialization starts in `i40e_init_dcb()`: it checks DCB capability, reads LLDP admin status from persistent FW LLDP NVM data or older LLDP config storage, rejects disabled LLDP, reads current DCBX status, fetches DCB config when status is done or in progress, and optionally enables MIB-change events. `i40e_get_dcb_config()` chooses IEEE-only behavior for older XL710 firmware, a legacy CEE v1 response for XL710 4.33, or the newer CEE response otherwise; CEE `ENOENT` falls back to IEEE LLDP MIB retrieval. Remote MIB absence is explicitly non-fatal.

LLDP parsing is streaming and TLV-driven. Organization TLVs are identified by OUI: IEEE 802.1Qaz TLVs are parsed by subtype, while CEE TLVs parse up to `I40E_CEE_MAX_FEAT_TYPE` nested feature TLVs. Serialization runs the inverse path: `i40e_dcb_config_to_lldp()` iterates a fixed TLV id sequence for ETS config, ETS recommendation, PFC config, and app priority, appending only TLVs with non-zero length.

Software DCB register programming is split into small helpers. The packet-buffer path first computes target sizes and watermarks in `i40e_dcb_hw_calculate_pool_sizes()`, then `i40e_dcb_hw_rx_pb_config()` programs decreasing watermarks before pool-size changes and increasing watermarks after pool-size changes to preserve hardware ordering requirements.

## State And Persistence

Primary persistent driver state is `hw->local_dcbx_config`, `hw->desired_dcbx_config`, `hw->remote_dcbx_config`, and `hw->dcbx_status`. Persistent LLDP admin status is read from NVM or firmware settings; local DCB updates are persisted into firmware LLDP MIB through admin queue calls, not into local files. Hardware state is written directly through `rd32()`/`wr32()` to port DCB, packet-buffer, and PFC registers.

## Dependencies And Integration Points

The file depends on `i40e_adminq.h`, `i40e_alloc.h`, `i40e_dcb.h`, `i40e_prototype.h`, LLDP/DCBX constants from `i40e_type.h`, and Linux bitfield helpers. It integrates with firmware admin queue calls such as `i40e_aq_get_lldp_mib()`, `i40e_aq_set_lldp_mib()`, `i40e_aq_get_cee_dcb_config()`, `i40e_aq_cfg_lldp_mib_change_event()`, NVM access helpers, and low-level register access macros.

## Risks

- TLV parsing trusts the firmware-provided LLDPDU buffer shape within the global `I40E_LLDPDU_SIZE`; malformed lengths can truncate parsing but there is limited per-sub-TLV validation.
- `i40e_dcb_config_to_lldp()` assumes the caller provided a zeroed buffer; an app TLV with zero apps leaves length zero and relies on prior buffer contents being harmless.
- `i40e_dcb_hw_rx_up2tc_config()` ORs new mapping bits into the existing register value without clearing all UP-to-TC fields first.
- Packet-buffer sizing logs but does not fill `pb_cfg` when shared pool size is negative.
- DCB behavior is firmware-version specific, especially around XL710 4.33 and older firmware branches.

## Test Signals

Useful tests include synthetic IEEE and CEE LLDPDU parser fixtures, round-trip serialization checks for ETS/PFC/app TLVs, firmware-mocked `ENOENT` fallback tests, DCB init tests for enabled/disabled LLDP admin status, register programming tests that verify mask/field writes, and hardware or emulator tests for PFC and packet-buffer programming under 1/2/4-port and low/high TC counts.
