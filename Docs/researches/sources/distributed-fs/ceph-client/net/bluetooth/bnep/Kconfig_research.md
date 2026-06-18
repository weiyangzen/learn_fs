# sources/distributed-fs/ceph-client/net/bluetooth/bnep/Kconfig

## Purpose
This Kconfig file defines build options for the Bluetooth Network Encapsulation Protocol layer.

## Important APIs, Types, And Functions
Symbols are `BT_BNEP`, `BT_BNEP_MC_FILTER`, and `BT_BNEP_PROTO_FILTER`. `BT_BNEP` is a tristate that depends on classic Bluetooth BR/EDR and selects CRC32. The filter options are bool features gated by `BT_BNEP`.

## Control Flow
The selections determine whether the BNEP module is built and whether multicast and protocol filter code is compiled in `core.c` and `netdev.c`.

## State, Persistence, And Dependencies
There is no runtime state. Build dependencies ensure the classic Bluetooth transport and CRC32 helper are present for PAN Ethernet emulation.

## Integration Points
`net/bluetooth/Kconfig` sources this file, and `bnep/Makefile` builds `bnep.o` when `BT_BNEP` is enabled.

## Risks
Disabling filter options changes control-message behavior: peers receive unsupported-filter responses and local netdev filtering is absent. Dependency mistakes could build PAN support without classic Bluetooth L2CAP support.

## Test Signals
Build and runtime signals include presence or absence of `bnep.ko`, `bt-proto-4` alias registration, and filter control responses matching selected options.
