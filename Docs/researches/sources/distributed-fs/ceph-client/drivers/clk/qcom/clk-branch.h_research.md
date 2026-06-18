# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-branch.h

## Purpose
Declares Qualcomm branch gate descriptors, CBCR bit definitions, inline CBCR field helpers, exported branch ops, and container helpers. It is the static data contract for branch clocks used by Qualcomm clock controller drivers.

## Important APIs, Types, And Functions
Key types are `struct clk_branch` and `struct clk_mem_branch`. Halt modes include `BRANCH_HALT`, `BRANCH_HALT_ENABLE`, voted variants, `BRANCH_HALT_DELAY`, and `BRANCH_HALT_SKIP`. CBCR definitions include `CBCR_CLK_OFF`, `CBCR_NOC_FSM_STATUS`, memory force bits, wake/sleep fields, and `CBCR_CLOCK_ENABLE`. Inline helpers update force memory, wakeup, sleep, and enable fields.

## Control Flow
Clock controller data fills branch register addresses, bit numbers, halt policy, and the embedded `clk_regmap`. CCF calls the selected exported ops from `clk-branch.c`, which use the descriptor to toggle and poll hardware. Inline helpers are available to SoC-specific code that needs direct CBCR field programming.

## State And Persistence
No runtime state is owned by the header. Descriptor fields persist in static clock tables and determine how hardware state is interpreted. CBCR fields persist in MMIO registers and may affect memory retention and clock gating across consumer enable transitions.

## Dependencies And Integration Points
Includes CCF, bitfield helpers, and `clk-regmap.h`. It integrates with the larger Qualcomm common clock controller pattern where each branch is registered through `devm_clk_register_regmap()`.

## Risks And Edge Cases
The halt policy constants are compact numeric values with a voted bit overlay, so incorrect combinations can change polling semantics. Inline helpers take `struct clk_branch` by value; callers must pass descriptors with valid `halt_reg` and `regmap`.

## Test Signals
Static build coverage of CBCR helpers, runtime reads of `is_enabled`, and branch descriptors with all halt policies validate the header contract.
