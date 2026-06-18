# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_fdir.h

## Purpose
`txgbe_fdir.h` declares TXGBE Flow Director hash, ATR, mask, filter programming, configuration, and cleanup APIs.

## Important APIs, Types, and Functions
It declares `txgbe_atr_compute_perfect_hash()`, `txgbe_atr()`, `txgbe_fdir_set_input_mask()`, `txgbe_fdir_write_perfect_filter()`, `txgbe_fdir_erase_perfect_filter()`, `txgbe_configure_fdir()`, and `txgbe_fdir_filter_exit()`.

## Control Flow
There is no executable flow. TXGBE software init installs `txgbe_atr()` and `txgbe_configure_fdir()` callbacks, while ethtool code calls the mask/filter APIs.

## State and Persistence Behavior
The header owns no state. Implementations operate on `struct wx`, `struct wx_ring`, `struct wx_tx_buffer`, and `union txgbe_atr_input` hardware/software Flow Director state.

## Dependencies and Integration Points
It requires TXGBE ATR types from `txgbe_type.h` and shared ring types. It connects transmit path, ethtool RX NFC, and device configuration paths to Flow Director programming.

## Risks and Edge Cases
Callers must hold appropriate locks for perfect-filter list operations; the low-level functions only program hardware. API misuse can program filters while the device is down or before Flow Director mode is initialized.

## Test Signals
Build TXGBE and run transmit ATR plus ethtool perfect-filter operations that reach every declared function.
