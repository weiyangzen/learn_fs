# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-krait.h

## Purpose
Declares descriptor types and exported ops for Krait mux and divide-by-2 clocks backed by L2 indirect registers.

## Important APIs, Types, And Functions
`struct krait_mux_clk` carries parent mapping, indirect register offset, mask, shift, cached enable selection, low-power flag, safe/old parent state, reparent flag, errata flag, `clk_hw`, and notifier block. `struct krait_div2_clk` carries offset, width, shift, low-power flag, and `clk_hw`. The header exports `krait_mux_clk_ops`, `krait_div2_clk_ops`, and container helpers.

## Control Flow
Krait clock controller code embeds these structures, configures CCF init data on the contained `clk_hw`, and registers them with the exported ops. Runtime code in `clk-krait.c` performs all indirect register operations.

## State And Persistence
Static descriptor fields define how the indirect register is interpreted. Runtime fields such as `en_mask` and `reparent` persist parent-switch decisions across CCF callbacks and notifiers.

## Dependencies And Integration Points
Includes only CCF provider APIs. The implementation depends on Krait L2 accessors and is used by Krait CPU clock setup code.

## Risks And Edge Cases
The descriptor exposes several coordination fields (`safe_sel`, `old_index`, `clk_nb`) that external notifier code may rely on; inconsistent updates can desynchronize software parent state from hardware.

## Test Signals
Compile coverage with Krait CPU clock drivers and runtime parent/divider transitions verify the header contract.
