# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Makefile

## Purpose
`ath12k/Makefile` maps Kconfig symbols to the ath12k module object list. It defines the core object composition, optional feature objects, the AHB bus object, the Wi-Fi 7 subdirectory build, and a trace include path.

## Important Build Rules
- `obj-$(CONFIG_ATH12K) += ath12k.o` creates the main module.
- `ath12k-y` links core driver units: `core.o`, `hal.o`, `wmi.o`, `mac.o`, `reg.o`, `htc.o`, `qmi.o`, datapath TX/RX/HTT/peer/monitor objects, `debug.o`, `ce.o`, `peer.o`, `dbring.o`, `mhi.o`, `pci.o`, `fw.o`, and `p2p.o`.
- `ath12k-$(CONFIG_ATH12K_AHB) += ahb.o` conditionally includes platform AHB support.
- `obj-$(CONFIG_ATH12K) += wifi7/` always descends into the Wi-Fi 7 hardware-specific subdirectory when ath12k is enabled.
- Optional objects include debugfs/station/HTT stats, ACPI, trace, WoW PM, coredump, nl80211 testmode, and thermal support.
- `CFLAGS_trace.o := -I$(src)` lets generated trace code locate local `trace.h`.

## Control Flow And State Behavior
The Makefile has no runtime state, but its conditional object selection determines which callbacks and exported helpers exist. For example, `CONFIG_PM` controls `wow.o`, `CONFIG_ACPI` controls `acpi.o`, and `CONFIG_ATH12K_AHB` controls whether AHB register/remoteproc support is linked.

## Dependencies And Integration Points
This file is consumed by Kbuild and integrates with `Kconfig`, the local `wifi7/Makefile`, generated tracing infrastructure, and kernel conditional compilation. It must stay synchronized with source-file names and with config guards used in headers such as `acpi.h` and `wow.h`.

## Risks And Edge Cases
- Missing optional objects can produce unresolved symbols when headers expose non-stub declarations under the wrong config guard.
- Always building `wifi7/` with `CONFIG_ATH12K` means subdirectory build failures break all ath12k builds.
- Trace include flags are required for tracepoint generation; removing them can cause non-obvious build failures.

## Test Signals
Run build matrixes for `CONFIG_ATH12K=m/y`, `CONFIG_ATH12K_AHB`, `CONFIG_ACPI`, `CONFIG_PM`, `CONFIG_ATH12K_DEBUGFS`, `CONFIG_ATH12K_TRACING`, `CONFIG_ATH12K_COREDUMP`, `CONFIG_NL80211_TESTMODE`, and `CONFIG_THERMAL`.
