# sources/distributed-fs/ceph-client/net/bluetooth/Makefile

## Purpose
This Makefile maps Bluetooth Kconfig symbols to built objects and protocol subdirectories.

## Important APIs, Types, And Functions
It builds `bluetooth.o` from core objects such as `af_bluetooth.o`, HCI core/conn/event/socket/sysfs/sync/driver code, L2CAP, SMP, management, ECDH helper, codec, EIR, and utility files. It adds optional objects for coredumps, SCO, ISO, LEDs, Microsoft extensions, AOSP extensions, debugfs, and selftests. It also builds RFCOMM, BNEP, HIDP, and `bluetooth_6lowpan.o` when enabled.

## Control Flow
There is no runtime control flow. Build-time object inclusion follows `obj-$(CONFIG_...)` and `bluetooth-$(CONFIG_...)` assignments.

## State, Persistence, And Dependencies
The file has build-system state only. It depends on Kconfig symbols defined in the Bluetooth tree and driver/device-coredump configs.

## Integration Points
The top-level kernel build consumes this file. Its object grouping must stay aligned with exported symbols and init/exit ordering in source files such as `af_bluetooth.c`, `6lowpan.c`, `bnep/core.c`, and optional extension helpers.

## Risks
Missing an object here can produce unresolved symbols for headers that compile fine. Adding optional objects to the wrong aggregate can make disabled features link into the core unexpectedly. Ordering within `bluetooth-y` matters when initcall dependencies or duplicate symbols appear.

## Test Signals
Build tests across config matrices should verify expected objects appear, modules load, and optional files such as `coredump.o`, `aosp.o`, `hci_codec.o`, and `6lowpan.o` are only present for matching symbols.
