<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.c

## Purpose
Adds DWMAC5/EQoS 5.x features used by DWMAC510 ops: automotive safety/ECC/parity handling, RX parser table programming, and flexible PPS output configuration.

## Important APIs, Types, And Functions
Exports `dwmac5_safety_feat_config`, `dwmac5_safety_feat_irq_status`, `dwmac5_safety_feat_dump`, `dwmac5_rxp_config`, and `dwmac5_flex_pps_config`. Internal error descriptor tables map MAC/MTL/DMA safety bits to stat offsets and log strings. RX parser helpers disable/enable parser and update internal RAM entries.

## Control Flow
Safety config enables ECC/address override and interrupt bits based on ASP level and optional config, then enables FSM parity/timeout and data parity protection for higher ASP levels. Safety IRQ status reads MTL/DMA summary bits, dispatches MAC/MTL/DMA handlers, clears detailed status registers, logs each set bit, updates stats, and returns nonzero on uncorrectable errors. RX parser config disables MAC RX, disables parser, clears `in_hw`, programs entries by priority plus fragments, appends last/pass entry, writes NPE/NVE, enables parser, and restores RX. PPS config validates busy/sub-second inputs, disables or sets target time, interval, width, and activate command.

## State And Persistence
State lives in safety control/status registers, `stmmac_safety_stats`, RX parser table RAM, `stmmac_tc_entry` metadata (`in_hw`, `table_pos`), PPS registers, and MAC RX enable state. No disk persistence exists.

## Dependencies And Integration Points
Depends on DWMAC4/5 registers, STMMAC TC entries, PTP time flags, netdev logging, and DWMAC510 ops table in `dwmac4_core.c`.

## Risks
Safety log uses bit positions as stat array offsets; layout coupling with `stmmac_safety_stats` is strict. RX parser temporarily disables RX and must restore prior MAC config on all paths. `min_prio_idx` is only valid if `found`. PPS period math divides by `sub_second_inc` and rejects too-small periods after programming some state.

## Test Signals
Safety config for ASP 0/1/2/3, correctable vs uncorrectable IRQ handling and stats, invalid dump indexes, RX parser entry ordering/fragments/last entry, no-entry path, RX restore after update failure, PPS enable/disable, busy target rejection, binary vs digital rollover nanosecond conversion, and FPE users of DWMAC510 ops are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.c -->
