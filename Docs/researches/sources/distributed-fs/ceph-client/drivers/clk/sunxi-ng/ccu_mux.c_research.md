# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_mux.c

## Purpose
`ccu_mux.c` implements parent selection helpers and standalone mux clock ops for sunxi-ng clocks, including fixed/variable predivider support and safe reparenting notifiers.

## Important APIs, Types, And Functions
Important APIs are `ccu_mux_helper_apply_prediv()`, `ccu_mux_helper_determine_rate()`, `ccu_mux_helper_get_parent()`, `ccu_mux_helper_set_parent()`, exported `ccu_mux_ops`, and `ccu_mux_notifier_register()`.

## Control Flow
Rate determination iterates parents unless `CLK_SET_RATE_NO_REPARENT` is set, applies predividers, delegates class-specific rounding, unapplies predividers for parent-rate requests, and chooses the best rate. Parent changes apply optional sparse tables, key-field unlock values, and update bits under the CCU lock. Notifiers temporarily switch to a bypass parent before PLL rate changes and restore after.

## State And Persistence
State is hardware mux fields plus `ccu_mux_nb.original_index` during notifier callbacks. No persistent storage exists.

## Dependencies And Integration Points
Dependencies include CCF, delay, MMIO, gates, common feature flags, and consumers from every compound clock class.

## Risks
Risks include incorrect sparse mux tables, predivider handling, key-field writes, and notifier delay/bypass configuration. A bad parent switch can destabilize CPU or bus clocks during PLL changes.

## Test Signals
Test with clock parent changes, rate requests across parent choices, CPU/PLL notifier paths, and clock-summary parent/rate verification.
