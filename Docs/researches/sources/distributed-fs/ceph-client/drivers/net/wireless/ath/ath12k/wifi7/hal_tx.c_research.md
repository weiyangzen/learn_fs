# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_tx.c

## Purpose

`hal_tx.c` implements Wi-Fi 7 transmit HAL helpers for TCL data command descriptor setup and DSCP-to-TID table programming. It is the bridge between software TX metadata (`struct hal_tx_info`) and the little-endian TCL command words consumed by hardware.

## Important APIs And Functions

`ath12k_wifi7_hal_tx_cmd_desc_setup()` fills a `struct hal_tcl_data_cmd` with DMA buffer address, return buffer manager, software cookie, descriptor type, bank ID, command metadata, packet length, packet offset, TID, PMAC/LMAC ID, VDEV ID, and AST search information. `ath12k_wifi7_hal_tx_set_dscp_tid_map()` programs a hardware DSCP/TID table for a selected map ID. The internal `dscp2tid()` helper maps DSCP classes to TIDs with `dscp >> 3`.

## Control Flow

TX descriptor setup is straightforward field packing: address low and high words are encoded first, then descriptor identity and command metadata are encoded into `info0` through `info5`. The DSCP/TID setup path reads the TCL common control register, sets `HAL_TCL1_RING_CMN_CTRL_DSCP_TID_MAP_PROG_EN`, builds the 64-entry DSCP table as packed 3-bit TID values, writes it four bytes at a time to `HAL_TCL1_RING_DSCP_TID_MAP` plus the selected table offset, then clears the programming-enable bit.

## State And Persistence Behavior

`ath12k_wifi7_hal_tx_cmd_desc_setup()` only initializes transient ring descriptors. `ath12k_wifi7_hal_tx_set_dscp_tid_map()` persists state in TCL hardware registers until reset or reprogramming, affecting later hardware classification for the selected DSCP/TID map ID. There is no file-local persistent software state.

## Dependencies And Integration

The file includes Wi-Fi 7 HAL TX definitions, generic HAL/HIF headers, and uses `ath12k_hif_read32()`/`ath12k_hif_write32()` for MMIO. It is referenced through `hal_ops.tx_set_dscp_tid_map` in chip HAL ops and by DP TX code that prepares TCL descriptors. The command format depends on `hal_desc.h` bit masks and the `hal_tcl_data_cmd` ABI.

## Risks And Edge Cases

The DSCP packing loop stores 8 three-bit mappings into three bytes by copying from a host-endian `u32` into a byte array, then writing as `u32`; this is conventional for the target layout but endian-sensitive and should be treated as hardware ABI. The table `id` is not range-checked in this helper, so callers must pass a valid hardware table index. Descriptor setup trusts `hal_tx_info` fields; invalid DMA addresses, lengths, offsets, bank IDs, or RBM IDs will be sent directly to hardware.

## Test Signals

Build coverage should catch field-mask drift. Runtime signals include successful TCP/UDP TX on all TCL rings, correct WMM/TID behavior for DSCP-marked traffic, no stuck TCL rings, no WBM release cookie mismatches, and correct packet completion routing across all configured TX banks.
