<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Makefile

## Purpose
This Makefile builds the Quantenna qtnfmac common FullMAC driver and PCIe transport module.

## Important APIs, Types, And Functions
It adds include flags for the qtnfmac directory, builds `qtnfmac.o` from common objects (`core.o`, `commands.o`, `trans.o`, `cfg80211.o`, `event.o`, `util.o`, `qlink_util.o`), and builds `qtnfmac_pcie.o` from shared-memory IPC and PCIe platform objects. Debugfs support adds `debug.o` to the PCIe module when enabled.

## Control Flow
Kbuild links common cfg80211/command/event/transport functionality into the common module and hardware/transport-specific code into the PCIe module according to the relevant config symbols.

## State And Persistence
No runtime state exists. The file defines module composition and include path state.

## Dependencies And Integration Points
Driven by `CONFIG_QTNFMAC` and `CONFIG_QTNFMAC_PCIE`, and consumed by Kbuild under the Quantenna vendor directory.

## Risks
Common and bus-specific module boundaries must stay aligned with exported symbols. Missing a new common object can produce unresolved symbols in PCIe or incomplete cfg80211 behavior. Debugfs object is transport-specific here.

## Test Signals
Build both built-in and module configurations, with and without DEBUG_FS, and confirm common and PCIe modules link without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Makefile -->
