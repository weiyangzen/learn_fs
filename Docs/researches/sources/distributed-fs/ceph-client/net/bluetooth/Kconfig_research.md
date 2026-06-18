# sources/distributed-fs/ceph-client/net/bluetooth/Kconfig

## Purpose
This Kconfig file defines top-level Bluetooth subsystem options and includes subordinate protocol and driver configuration menus.

## Important APIs, Types, And Functions
Main symbols are `BT`, `BT_BREDR`, `BT_LE`, `BT_LE_L2CAP_ECRED`, `BT_6LOWPAN`, `BT_LEDS`, `BT_MSFTEXT`, `BT_AOSPEXT`, `BT_DEBUGFS`, `BT_SELFTEST`, `BT_SELFTEST_ECDH`, `BT_SELFTEST_SMP`, and `BT_FEATURE_DEBUG`. It also sources RFCOMM, BNEP, HIDP, and drivers Bluetooth Kconfigs.

## Control Flow
Kconfig selection determines which object files and feature paths are compiled. `BT` selects core crypto primitives used by pairing and management; `BT_BREDR` and `BT_LE` gate classic and LE protocol families; `BT_6LOWPAN` depends on LE and generic 6LoWPAN; extension and debug options enable optional source files in the Makefile.

## State, Persistence, And Dependencies
The file has no runtime state. It encodes build-time dependencies on RFKILL, CRC16, crypto algorithms, debugfs, LED triggers, LE support, and debug kernel support for selftests.

## Integration Points
`net/bluetooth/Makefile` consumes these symbols to build `bluetooth.o`, `bluetooth_6lowpan.o`, optional extension modules, and subdirectories. User-visible configuration controls which socket protocols, HCI features, debugfs entries, and selftests exist.

## Risks
Incorrect dependency changes can create link failures or expose runtime code without required crypto or transport support. Enabling selftests can delay boot or module load. Feature combinations such as `BT_AOSPEXT`, `BT_MSFTEXT`, `BT_LE`, and `BT_BREDR` should be tested both built-in and modular.

## Test Signals
Important signals are successful allmodconfig/allyesconfig/minimal builds, expected module lists for selected options, crypto dependencies present when `BT` is enabled, and runtime feature availability matching selected symbols.
