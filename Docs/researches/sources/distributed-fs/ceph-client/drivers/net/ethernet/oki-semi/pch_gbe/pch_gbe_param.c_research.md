# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_param.c

## Purpose
Implements module parameter parsing and validation for PCH GBE descriptor counts, speed, duplex, autoneg advertisement, flow control, and checksum offload defaults.

## Important APIs, Types, And Functions
Module parameters: `TxDescriptors`, `RxDescriptors`, `Speed`, `Duplex`, `AutoNeg`, `FlowControl`, `XsumRX`, `XsumTX`. `struct pch_gbe_option` models enable/range/list validation. `pch_gbe_validate_option()`, `pch_gbe_check_copper_options()`, and `pch_gbe_check_options()` apply policy.

## Control Flow
Unset options become defaults. Descriptor counts are range-checked and rounded. Checksum options clear netdev feature bits when disabled. Flow control chooses a PCH mode. Speed/duplex/autoneg combinations either constrain advertised modes or force supported 10/100 modes; 1000 half duplex falls back to 1000 full-duplex autoneg.

## State And Persistence
Mutates ring counts, `netdev->features`, MAC flow-control/autoneg/speed/duplex fields, and PHY advertisement state. Runtime module-load state only.

## Dependencies And Integration Points
Depends on `pch_gbe.h`, module parameters, netdev feature bits, speed/duplex constants, and probe ordering.

## Risks And Edge Cases
Parameters are global, not per-device. Invalid values are defaulted with debug-only visibility. Forced link policy must remain consistent with later ethtool changes.

## Test Signals
Load with boundary/invalid values, check ring counts via ethtool, verify advertised/forced link modes, and inspect checksum features with `ethtool -k`.
