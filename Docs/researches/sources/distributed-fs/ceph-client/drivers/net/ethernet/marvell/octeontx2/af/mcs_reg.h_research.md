# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_reg.h

## Purpose

`mcs_reg.h` is the MCS register offset map. It defines the MMIO addresses used by the common and CNF10KB MCS drivers for top-level control, MIL/HIL/link setup, PAB/PEX parser configuration, BBE/PAB interrupts, CPM flow/SecY/SC/SA/PN tables, CSE statistics, and top-level interrupt routing.

## Important APIs, Types, And Constants

Top-level and link macros include `MCSX_IP_MODE`, `MCSX_MCS_TOP_SLAVE_PORT_RESET()`, `MCSX_MCS_TOP_SLAVE_CHANNEL_CFG()`, `MCSX_MIL_GLOBAL`, `MCSX_MIL_RX_LMACX_CFG()`, `MCSX_HIL_GLOBAL`, `MCSX_LINK_LMACX_CFG()`, `MCSX_MIL_RX_GBL_STATUS`, and `MCSX_MIL_IP_GBL_STATUS`.

PAB/PEX macros cover port modes, FIFO skid config, VLAN/custom tag config, parser ethertype enable, PTP/custom header skip config, and control packet rule registers: ethertype rules, DA rules, DA-range rules, combo rules, MAC rule, and rule enable.

BBE/PAB interrupt macros define status, enable, and interrupt rewrite registers for RX/TX BBE and PAB paths plus overflow detail registers. CPM macros define RX/TX flow TCAM data/mask/enable registers, RX SC CAM and enable registers, RX/TX SecY map and policy registers, SA map/policy/PN table registers, PN/XPN thresholds, TX active-SA and SA valid registers, and CNF10KB auto-rekey registers.

CSE macros define RX/TX counter locations for SecY, SC, SA, flow ID, and port statistics, plus stats clear/control registers. Top-level interrupt macros include `MCSX_IP_INT`, `MCSX_IP_INT_ENA_W1S`, `MCSX_IP_INT_ENA_W1C`, `MCSX_TOP_SLAVE_INT_SUM`, `MCSX_TOP_SLAVE_INT_SUM_ENB`, and CPM child interrupt registers.

## Control Flow

The header has no runtime functions, but many macros are GNU statement expressions that compute offsets dynamically from the lexical `mcs` pointer. Most macros choose one base address for single-block CN10KB (`mcs->hw->mcs_blks == 1`) and another for multi-block CNF10KB. Driver code then adds resource indices and register-bank indices to those bases before calling `mcs_reg_read()` or `mcs_reg_write()`.

Control packet rule programming in `mcs.c` depends on the rule-offset layout in this header. Stats routines map each mailbox stats type to the corresponding CSE counter macro. Interrupt handling reads top-level and child status registers from this header and clears them by writing the same status value back.

## State And Persistence Behavior

The header defines where hardware state lives, not the state itself. Register groups correspond to persistent device programming: parser tag config, flow TCAM contents and masks, resource enable bits, SecY/SC/SA/PN policy memory, thresholds, stats controls, and interrupt enables. Counter registers are read-only from the software perspective except for clear/control sequences.

## Dependencies And Integration Points

`mcs_reg.h` includes `<linux/bits.h>` and depends on a local variable named `mcs` being in scope for most statement-expression macros. It is tightly coupled to `struct mcs->hw->mcs_blks` from `mcs.h`. The common driver and CNF10KB variant both include it; incorrect offsets affect all mailbox operations.

## Risks

The lexical dependency on `mcs` makes the macros concise but fragile: using them in a helper without a variable named `mcs` will fail to compile, and using a different `mcs` than intended will silently compute the wrong family layout. Register definitions mix dynamic offsets with fixed CN10KB-only and CNF10KB-only addresses; shared code must know when fixed `_ENA_1`, active-SA, and custom-tag registers are valid.

Several enable-register users support resources above 63 but the register macros only select the second register; the caller must also normalize bit positions. If callers pass raw IDs to `BIT_ULL()`, high-index entries can be enabled or disabled incorrectly.

Because these constants directly encode hardware ABI, any drift from the data sheet can cause silent corruption of MACsec policy memory, wrong stats, missed interrupts, or traffic bypass/drop behavior.

## Test Signals

Good signals include successful probe on both register layouts, correct hardware-info-derived capacities, parser config visible in custom tag registers, successful flow/SecY/SC/SA programming and packet hits, accurate stats by type and direction, working PN threshold interrupts, correct BBE/PAB fatal reporting, and no MMIO faults or nonsensical counter values when exercising both CN10KB and CNF10KB paths.
