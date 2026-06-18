# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/Makefile

## Purpose
This Makefile defines the object composition for the Marvell PPv2 Ethernet driver. It builds the composite `mvpp2.o` module or built-in object when `CONFIG_MVPP2` is enabled and conditionally adds PTP support when `CONFIG_MVPP2_PTP` is selected.

## Important APIs, Types, and Functions
There are no C APIs in this file. The important build contracts are:
- `obj-$(CONFIG_MVPP2) := mvpp2.o`
- `mvpp2-y := mvpp2_main.o mvpp2_prs.o mvpp2_cls.o mvpp2_debugfs.o`
- `mvpp2-$(CONFIG_MVPP2_PTP) += mvpp2_tai.o`

## Control Flow
Kbuild evaluates the config symbols and links the listed objects into the single PPv2 driver object. The classifier (`mvpp2_cls.o`), parser (`mvpp2_prs.o`), main driver (`mvpp2_main.o`), and debugfs support (`mvpp2_debugfs.o`) are always part of the driver when PPv2 is enabled. Timestamp/TAI code is included only for PTP-enabled builds.

## State and Persistence
The file holds build-time state only. It does not create runtime state, but it determines whether runtime PTP hooks in `mvpp2.h` resolve to real functions or inline stubs.

## Dependencies and Integration Points
It integrates with Linux Kbuild and the `CONFIG_MVPP2` / `CONFIG_MVPP2_PTP` Kconfig symbols. The listed object files depend on each other through shared headers such as `mvpp2.h`, `mvpp2_prs.h`, and `mvpp2_cls.h`.

## Risks and Edge Cases
Missing an object here can create link errors or silently remove features. `mvpp2_debugfs.o` is always linked with the driver, so debugfs-related code must remain safe even when debugfs is disabled or unavailable at runtime. Conditional PTP object inclusion must stay synchronized with the `CONFIG_MVPP2_PTP` stubs in `mvpp2.h`.

## Test Signals
Build the driver with `CONFIG_MVPP2` disabled, built-in, and modular; then repeat with `CONFIG_MVPP2_PTP` both disabled and enabled. Link success, absence of unresolved PTP symbols, and successful module load/probe are the primary signals.
