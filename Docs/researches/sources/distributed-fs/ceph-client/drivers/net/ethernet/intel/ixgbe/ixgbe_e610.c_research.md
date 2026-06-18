# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_e610.c

## Purpose

`ixgbe_e610.c` adds E610-specific hardware support to the ixgbe driver. It is the firmware-mediated control layer for Intel E610 adapters, centered on the Admin Command Interface (ACI), and binds E610 implementations into the common ixgbe MAC, PHY, and EEPROM operation tables. The file covers command transport over PF HICR/HIDA/HIBA registers, firmware event retrieval, common-resource arbitration, device/function capability discovery, link/media and flow-control setup, EEPROM/NVM/flash-bank access, reset behavior, PBA string reads, and `libie_fwlog` integration.

This file is not packet data-path code. Its callers are mostly probe/open/reset/link/ethtool paths and generic ixgbe operation callbacks. The data it persists lives in `struct ixgbe_hw` substructures such as `hw->aci`, `hw->dev_caps`, `hw->func_caps`, `hw->link`, `hw->phy`, `hw->fc`, `hw->eeprom`, `hw->flash`, and `hw->fwlog`.

## Important APIs, types, and functions

Key APIs are `ixgbe_aci_send_cmd()`, `ixgbe_aci_get_event()`, `ixgbe_acquire_res()`, `ixgbe_release_res()`, `ixgbe_get_caps()`, `ixgbe_aci_get_phy_caps()`, `ixgbe_aci_get_link_info()`, `ixgbe_setup_phy_link_e610()`, `ixgbe_check_link_e610()`, `ixgbe_setup_fc_e610()`, `ixgbe_read_flat_nvm()`, `ixgbe_read_ee_aci_e610()`, `ixgbe_get_flash_data()`, `ixgbe_reset_hw_e610()`, `ixgbe_fwlog_init()`, and `ixgbe_fwlog_deinit()`. The file also defines `mac_ops_e610`, `phy_ops_e610`, `eeprom_ops_e610`, and exported `ixgbe_e610_info`.

The implementation depends on `libie_aq_desc` and ACI constants, E610 command data structures in `ixgbe_type.h`, generic ixgbe helpers from common/X540/X550 code, Linux mutex/allocation/polling helpers, and register access macros.

## Control flow

ACI command flow starts with a descriptor initialized by `ixgbe_fill_dflt_direct_cmd_desc()`. `ixgbe_aci_send_cmd()` optionally snapshots retryable descriptors and buffers, serializes access with `hw->aci.lock`, and calls `ixgbe_aci_send_cmd_execute()`. The execute helper validates HICR state, writes optional indirect buffers to HIBA, writes descriptor dwords to HIDA, sets `PF_HICR.C`, polls for completion, reads response descriptors, checks opcode and firmware return value, copies response data back, and updates `hw->aci.last_status`. Selected link-related opcodes retry on firmware busy.

Capability discovery sends `list_dev_caps` and `list_func_caps` into a 4 KiB buffer, then parses common resources such as valid functions, SR-IOV, VMDq, DCB, RSS table size, RX/TX queue ranges, MSI-X vectors, pending NVM update flags, MTU, reset restrictions, and topology image metadata. Link flow is firmware owned: `ixgbe_aci_get_link_info()` updates cached link state, speed, PHY type bitmaps, media availability, FEC, topology conflict, pacing, LSE state, and negotiated flow control. PHY setup reads supported and active configs, intersects requested advertised speeds with supported PHY type masks, and writes new config only when changed.

NVM and flash flow uses firmware resource ownership unless blank NVM mode leaves the flash lock unset. Shadow RAM and flat NVM reads are chunked to 4 KiB ACI transfers. `ixgbe_get_flash_data()` reads SR size, detects blank mode, discovers flash size by bisection, determines active/inactive NVM/OROM/netlist banks, and populates active version metadata. Reset flow stops the adapter, clears pending TX, takes SW/FW sync, writes `IXGBE_CTRL_RST`, polls for reset completion, handles double-reset recovery, restores RX packet buffer sizing, MAC address, RAR count, receive addresses, and LAN ID.

## State and persistence behavior

`hw->aci.last_status` persists the last firmware status, and `hw->aci.lock` serializes the CSR command path. Capability discovery populates `hw->dev_caps` and `hw->func_caps`; link/PHY operations mutate `hw->link`, `hw->phy`, and `hw->fc`; EEPROM/flash operations populate `hw->eeprom` and `hw->flash`. NVM write/update/erase/activate commands affect persistent device flash. PHY configuration, low-power mode, event masks, LEDs, and RX disable state affect hardware/firmware state until reset or reconfiguration.

## Dependencies and integration points

The exported `ixgbe_e610_info` is used during device binding and reuses many generic/X540/X550 helpers while overriding E610-specific firmware behavior. `ixgbe_ethtool.c` reaches this file for E610 LED identification, pause behavior, firmware version refresh, and generic operation callbacks. `libie_fwlog` sends commands through `__fwlog_send_cmd()`. NVM update tooling and ethtool EEPROM paths depend on the read/update/activate helpers.

## Risks and edge cases

`ixgbe_aci_send_cmd()` allocates a retry buffer but initially copies only one byte before using it to restore `buf_size` bytes on retry, which is suspicious for indirect commands. `ixgbe_discover_dev_caps()` and `ixgbe_discover_func_caps()` return `0` even if the ACI list command fails, potentially masking capability discovery failures. ACI polling can block control-plane callers for long intervals. Media detection reports unknown for multiple PHY bits and uses highest-bit heuristics when link is down. NVM reads may partially update caller buffers before failure. Reset polls the reset bit for only ten 1 usec iterations. Flash bank offset zero is treated as invalid.

## Test signals

Useful validation includes successful E610 probe, firmware version population, nonzero device/function capabilities, correct ethtool link modes, link status events, pause mode changes after reinit, EEPROM checksum validation, active/inactive flash version reads, fwlog debugfs initialization, ACI busy retry behavior, blank NVM mode handling, NVM lock contention, no-media module identification, and RX-disable fallback when the firmware command fails.
