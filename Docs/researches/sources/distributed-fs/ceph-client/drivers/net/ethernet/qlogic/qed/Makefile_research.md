# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/Makefile

## Purpose
This Makefile defines how the QLogic/Marvell `qed` core driver is built by Kbuild. It creates the `qed.o` module/object when `CONFIG_QED` is enabled and lists the base object files plus optional protocol and virtualization objects gated by Kconfig symbols.

## Important Build Entries
- `obj-$(CONFIG_QED) := qed.o` makes the composite driver conditional on `CONFIG_QED`.
- `qed-y` includes core objects such as chain management, context management, DCBX, debug, devlink, hardware access, firmware init ops, interrupts, L2, main, MCP, management TLV, PTP, selftest, slowpath commands, and SPQ.
- Optional `qed-$()` entries add FCoE, iSCSI, LL2, OOO, NVMe/TCP, RDMA/iWARP/RoCE, and SR-IOV/VF support.

## Control Flow
There is no runtime control flow. Kbuild evaluates configuration symbols and appends matching objects to the composite `qed.o` link. Base objects are always included with `CONFIG_QED`; optional objects are included only when their symbols are enabled.

## State and Persistence
The Makefile persists build composition, not runtime state. Its ordering affects which translation units are compiled and linked into `qed.o`, which determines available symbols and feature coverage for the driver.

## Dependencies and Integration Points
This file integrates with Linux Kbuild and QED Kconfig symbols. It must stay synchronized with source files, exported symbols, and feature conditionals in headers such as `qed.h` and public headers under `include/linux/qed/`.

## Risks and Edge Cases
- Missing an object can cause link failures or runtime feature absence.
- Adding optional objects without the correct `CONFIG_` guard can pull in unavailable dependencies.
- Object composition must match protocol feature conditionals.
- The SPDX license expression matches the dual-licensed QED sources.

## Test Signals
Build matrix coverage is the key signal: `CONFIG_QED=y/m`, with and without FCoE, iSCSI, LL2, OOO, NVMETCP, RDMA, and SR-IOV. Linker errors, modpost warnings, and missing exported-symbol diagnostics identify composition regressions.
