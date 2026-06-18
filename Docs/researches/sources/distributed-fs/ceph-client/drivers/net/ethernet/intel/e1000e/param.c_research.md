# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/param.c

## Purpose
`param.c` defines and validates e1000e module parameters, converting per-board integer arrays and the global `copybreak` value into fields and flags on `struct e1000_adapter`. It centralizes user-configurable interrupt moderation, interrupt mode, PHY workarounds, NVM write protection, smart power down, and CRC stripping behavior used later by `netdev.c`.

## Important APIs, types, and functions
- Module parameters: `copybreak`, `TxIntDelay`, `TxAbsIntDelay`, `RxIntDelay`, `RxAbsIntDelay`, `InterruptThrottleRate`, `IntMode`, `SmartPowerDownEnable`, `KumeranLockLoss`, `WriteProtectNVM`, and `CrcStripping`.
- Parameter macros and limits: `E1000_MAX_NIC`, `OPTION_UNSET`, `OPTION_DISABLED`, `OPTION_ENABLED`, `E1000_PARAM_INIT`, `E1000_PARAM`, and per-option default/min/max constants.
- Validation model: `struct e1000_option` supports `enable_option`, `range_option`, and `list_option`; `e1000_validate_option()` applies defaults, validates ranges/lists/binary enable values, logs accepted settings, and replaces invalid values with defaults.
- Public entry point: `e1000e_check_options(struct e1000_adapter *adapter)` reads module parameter arrays at `adapter->bd_number`, validates values, and writes final settings into adapter fields.

## Control flow
At module load, Linux module-param machinery stores user-provided arrays and counts. During probe, after adapter flags are initialized, `e1000e_check_options()` runs for the adapter board number. If the board index exceeds `E1000_MAX_NIC`, it logs that defaults are used.

For each option, `e1000e_check_options()` builds a local `e1000_option`, checks whether the corresponding `num_*` count covers this board index, and either validates the user value or assigns the default. TX/RX delay options write `adapter->tx_int_delay`, `tx_abs_int_delay`, `rx_int_delay`, and `rx_abs_int_delay`; RX defaults switch to burst values when `FLAG2_DMA_BURST` is set.

`InterruptThrottleRate` has extra mode handling after range validation. Mode `0` disables ITR, `1` becomes dynamic mode with runtime value 20000, invalid special mode `2` falls back to default, `3` becomes dynamic conservative mode at 20000, `4` enables simplified 2000-8000 interrupt mode, and explicit numeric values clear low control bits in `itr_setting`.

`IntMode` chooses the best allowed interrupt mode based on `CONFIG_PCI_MSI` and `FLAG_HAS_MSIX`. With MSI support, it dynamically allocates an error/default string, defaults to MSI-X when hardware supports it and MSI otherwise, validates user input, and stores `adapter->int_mode`. Without MSI support, only legacy mode is valid.

Boolean options then set hardware-behavior flags or call workarounds: smart power down sets `FLAG_SMART_POWER_DOWN` only on capable devices; CRC stripping sets `FLAG2_CRC_STRIPPING` and `FLAG2_DFLT_CRC_STRIPPING`; Kumeran lock-loss calls `e1000e_set_kmrn_lock_loss_workaround_ich8lan()` for ICH8; write-protect NVM sets `FLAG_READ_ONLY_NVM` for ICH devices when enabled.

## State and persistence behavior
Module parameter values persist for the loaded module instance. `copybreak` is global and later used by RX cleaners to copy small packets into smaller skbs. Per-board arrays persist in static storage and are interpreted by board discovery order (`adapter->bd_number`).

The main state mutations are adapter fields and flags consumed by `netdev.c`: interrupt delay fields program hardware registers, `itr`/`itr_setting` control dynamic interrupt moderation, `int_mode` selects interrupt allocation, `FLAG_SMART_POWER_DOWN` affects PHY power behavior, `FLAG2_CRC_STRIPPING` affects RX CRC handling and jumbo support, and `FLAG_READ_ONLY_NVM` prevents writes on ICH paths. No NVM is written directly in this file.

## Dependencies and integration points
The file depends on Linux `module_param`, `module_param_array_named`, `MODULE_PARM_DESC`, PCI/device logging, allocation for dynamic strings, and e1000e internal definitions in `e1000.h`. Its output is consumed by probe, interrupt setup, TX/RX configuration, RX cleaners, reset, PHY workarounds, NVM write-protection code, and feature toggling.

## Risks and edge cases
- Board-number indexing means option arrays map by discovery order, not stable physical slot identity. Systems with more than `E1000_MAX_NIC` adapters silently use defaults for boards beyond the limit.
- Invalid values are logged and replaced with defaults; callers should not assume user input survived validation.
- `IntMode` allocates temporary strings under `CONFIG_PCI_MSI`; allocation failure exits `e1000e_check_options()` early, leaving later options unapplied.
- `InterruptThrottleRate` has special modes outside the normal numeric range, so validation logic deliberately treats values `0-4` differently from ordinary interrupt rates.
- Disabling NVM write protection is explicitly dangerous, because later NVM write paths can persistently corrupt EEPROM.
- CRC stripping interacts with BMC traffic, RXFCS, and jumbo-frame support on newer PCH hardware.

## Test signals
Useful tests include loading the module with valid, unset, and invalid values for every parameter; checking dmesg logs for accepted/defaulted settings; validating interrupt mode fallback on systems with and without MSI-X; verifying ITR dynamic/simple/off behavior through traffic and register inspection; checking `copybreak` effects on small RX packets; confirming CRC stripping/RXFCS/jumbo interactions; and ensuring write-protect flags are applied only to ICH adapters. Build coverage should include both `CONFIG_PCI_MSI` enabled and disabled.
