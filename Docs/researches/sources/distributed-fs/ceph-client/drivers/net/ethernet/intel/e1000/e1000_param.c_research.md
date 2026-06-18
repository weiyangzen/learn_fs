# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000/e1000_param.c

## Purpose
This file defines and validates legacy `e1000` module parameters. Its job is to translate per-adapter integer arrays supplied at module load into adapter settings for descriptor counts, speed/duplex/autonegotiation, flow control, checksum offload, interrupt moderation, and PHY smart power down.

## Important APIs, Types, and Functions
The `E1000_PARAM()` macro declares parameter arrays and `module_param_array_named()` metadata for up to `E1000_MAX_NIC` boards. `struct e1000_option` describes an enable, range, or list option. `e1000_validate_option()` applies defaults, validates ranges or enumerated values, and logs selected or invalid values. `e1000_check_options()` is the public entry point called during probe after queues and hardware type are known. Link-specific validation is delegated to `e1000_check_fiber_options()` and `e1000_check_copper_options()`.

## Control Flow
Probe assigns `adapter->bd_number`, allocates queues, then calls `e1000_check_options()`. The function checks whether a module parameter was provided for that board index. If present, it validates and stores it; otherwise it uses the option default. Descriptor counts are range-limited by MAC generation and aligned to required descriptor multiples, then copied to all rings. Flow control is stored in both `hw.fc` and `hw.original_fc`. InterruptThrottleRate has special modes: `0` disables, `1` dynamic, `3` dynamic conservative, `4` simplified 2000-8000 interrupts/sec, and other valid values become fixed rates with control bits masked out.

For fiber and internal serdes, Speed and Duplex are ignored, and AutoNeg values other than 1000/full are rejected. For copper, Speed, Duplex, and AutoNeg are validated together. Explicit speed/duplex combinations either force `hw.forced_speed_duplex` or set autonegotiation advertisement masks; incomplete inputs narrow autonegotiation to the requested speed or duplex. The function finally validates MDI/MDI-X compatibility through `e1000_validate_mdi_setting()`.

## State and Persistence
The declared module arrays are global module state populated by the kernel module parameter parser. Adapter-specific results are persisted for the lifetime of the device in `adapter->tx_ring[].count`, `adapter->rx_ring[].count`, `adapter->rx_csum`, interrupt delay fields, `adapter->itr`, `adapter->itr_setting`, `adapter->smart_power_down`, `adapter->fc_autoneg`, and `adapter->hw` link/flow-control fields. No files or NVM are written.

## Dependencies and Integration Points
This file depends on `e1000.h` for adapter, ring, MAC, PHY, descriptor, speed, duplex, and flow-control definitions. Its output feeds `e1000_main.c` ring allocation, RX checksum configuration, interrupt moderation register programming, link setup, and power behavior. It relies on kernel module parameter infrastructure and device logging helpers.

## Risks
Parameter handling is order-sensitive: it requires `adapter->hw.mac_type`, media type, and queue allocation to be initialized before validation. Bad descriptor ranges can waste memory or fail DMA allocation if bounds or alignment rules are changed incorrectly. Speed, Duplex, and AutoNeg interactions can silently force unexpected link modes if validation logic regresses. InterruptThrottleRate mode values overlap with fixed numeric values, so changes must preserve the special-case handling. Board index overflow falls back to defaults, which is safe but can surprise multi-port users.

## Test Signals
Useful tests are module-load permutations for each parameter, including invalid values, sparse per-board arrays, more than 32 adapters, old MAC types with 256-descriptor caps, newer MACs with 4096 descriptors, fiber versus copper link options, forced 10/100 modes, 1000/full autonegotiation, dynamic and fixed ITR settings, checksum offload toggles, and SmartPowerDownEnable. Runtime validation should confirm resulting ring sizes, link mode, ethtool advertised modes, and interrupt throttle register behavior.
