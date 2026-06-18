# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw-ops.h

## Purpose

`hw-ops.h` is the inline dispatch layer for ath9k hardware-family operations. It gives shared driver code stable function names while routing implementation details through `struct ath_hw_ops` and `struct ath_hw_private_ops`, which are populated by AR9002/AR9003 family attach code.

## Important APIs, Types, and Functions

The public hardware wrappers include PCI power-save, RX enable, descriptor linking, calibration, interrupt status, TX descriptor setup/status processing, duration lookup, antenna diversity configuration, and tx99 test helpers. These call `ath9k_hw_ops(ah)->...`.

Private hardware wrappers include hang checks, PHY frequency and spur handling, RF register setup, baseband init, channel register programming, INI processing, OLC init, RF mode/delta slope, RF bus request/done, chainmask restore, ANI control, noise-floor reads, init calibration, calibration setup, fast channel change, radar params, calibration settings, PLL control computation, mode gain register init, and ANI INI cache. These call `ath9k_hw_private_ops(ah)->...`.

Several wrappers are conditional or nullable. `ath9k_hw_tx99_set_txpower()`, BT antenna diversity, AIC support, `ath9k_olc_init()`, `ath9k_hw_set_rf_regs()`, chainmask restore, radar params, mode gain init, and ANI INI cache guard optional callbacks.

## Control Flow

The flow is simple but important: `ath9k_hw_init()` attaches family-specific ops, then the rest of the hardware core and driver call these static inline wrappers. For example, `ath9k_hw_reset()` calls private wrappers for INI processing, RF mode/frequency, delta slope, spur mitigation, baseband init, calibration, and radar configuration without needing to branch on chip family at every call site.

## State and Persistence Behavior

This header stores no state directly. Its behavior depends entirely on function pointers embedded in `struct ath_hw`: `ah->ops` and `ah->private_ops`. The correctness of every wrapper therefore depends on attach-time initialization matching the detected MAC revision and on optional callbacks being checked before use.

## Dependencies and Integration Points

It includes `hw.h` and is included by `hw.c` plus other ath9k code that needs hardware-family operations. It integrates with `ar9002_hw_attach_ops()`, `ar9003_hw_attach_ops()`, PHY attach helpers, calibration attach helpers, and optional BT coexistence support.

## Risks

Most wrappers do not check for NULL callbacks because the attach path is expected to provide mandatory operations. A missing mandatory function pointer becomes a crash at first use, often during reset or channel change. Optional wrappers must remain guarded. Since these are static inline functions, changes can affect many call sites at compile time and may not have a single symbol to trace at runtime. The division between public and private ops is a maintenance boundary; exposing private wrappers broadly makes chip-family abstractions easier to violate.

## Test Signals

Test by probing every supported AR9xxx family path, resetting and changing channels, running calibration/ANI, starting RX/TX, reading interrupts, and exercising optional features such as BT coexistence, tx99, antenna combining, radar/DFS, and fast channel change. Build coverage should include configurations with and without `CONFIG_ATH9K_BTCOEX_SUPPORT`.
