# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/regs.h

## Purpose

`regs.h` is the Chelsio T3 hardware register map and bitfield macro header. It provides symbolic register offsets (`A_*`), bit shifts (`S_*`), masks (`M_*`), value constructors (`V_*`), flags (`F_*`), and field extractors (`G_*`) for the SGE, PCI/PCIe, GPIO/debug, MC7 memory controllers, CIM, TP, ULP RX/TX, PM, MPS, CPL switch, SMB/I2C/MI/SF, PL, MC5, and XGMAC blocks. Driver implementation files use it as the authoritative MMIO programming vocabulary.

## Important APIs, types, and functions

This header declares macros rather than C functions or types. Major covered blocks include:

- SGE registers: `A_SG_CONTROL`, doorbells, GTS, context command/data/masks, response queue credits, interrupt cause/enable, queue thresholds, timer tick, and context bases.
- PCI/PCIe registers: `A_PCIX_*`, `A_PCIE_*`, PEX controls/errors, parity and bus error flags.
- Debug/GPIO: `A_T3DBG_GPIO_EN`, interrupt enable/cause, active-low controls used by LED/PHY interrupt handling and ethtool physical ID.
- MC7 memory controller: config, mode, DLL/ref timings, ECC, BIST, interrupt cause/enable, and base aliases for PMRX/PMTX/CM regions.
- CIM: boot, SDRAM, host interrupt, host access, and IBQ debug registers.
- TP: ingress/out config, TCP options, page manager, timers, RSS, MTU, traffic manager, PIO, reset, MIB, interrupt, trace/drop/proxy/embedded fields.
- ULP RX/TX: iSCSI/DDP/STag/RQ/PBL/TPT bounds, page-size fields, DMA weights, and interrupt bits.
- PM/MPS/CPL: packet memory RX/TX errors, MPS port config/parity, CPL switch interrupts and mapping.
- Management buses and PL: SMB, I2C, MI1, serial flash, top-level interrupt enable/cause/reset/revision.
- MC5: DB config, partition indexes, latency, interrupt bits, DBGI command/address/data/response, and TCAM command registers.
- XGMAC: TX/RX controls, exact match/hash filters, interrupt/status, FIFO config, SERDES/XAUI/RGMII, packet size, reset, port config, stats, and second MAC base.

## Control flow

There is no executable control flow. Control flow in implementation files is expressed by reading, writing, masking, and testing these macros through helpers such as `t3_read_reg()`, `t3_write_reg()`, and `t3_set_reg_field()`. For example, `cxgb3_main.c` uses `A_XGM_*` and `F_*` bits to enable MACs and clear link faults, `A_SG_*` for doorbells and interrupt causes, `A_TP_*` for offload/RSS/MTU/scheduler setup, and `A_PL_*` for top-level interrupt masking. `mc5.c` uses `A_MC5_*` and `V_/F_` helpers for TCAM initialization.

## State and persistence behavior

The header itself has no mutable state. Its macros address volatile MMIO hardware state. Some registers represent persistent-ish hardware configuration across driver runtime, such as queue contexts, TCAM partitions, memory bounds, and MAC settings, but they are reprogrammed by initialization and are not persisted by this header. Register reads may have side effects in hardware; users such as `get_regs()` in `cxgb3_main.c` intentionally avoid clear-on-read MAC statistics.

## Dependencies and integration points

`regs.h` is included by most low-level cxgb3 driver files, including `cxgb3_main.c`, `cxgb3_offload.c`, and `mc5.c`. It depends only on preprocessor constants and the SPDX license line. Its names must match the hardware manuals and the `common.h` helper code that performs register access. It is also indirectly part of user-observable diagnostics because ethtool register dumps and error logs derive offsets and flags from this map.

## Risks and edge cases

- A wrong shift, mask, flag, or offset can silently program hardware incorrectly; there is no type checking.
- Macro names are global within the translation unit and many are short (`S_ADDR`, `S_BUSY`, `S_DATA`), so include-order conflicts are possible.
- Some register offsets are block-relative or aliased, such as TP PIO table offsets and XGMAC second-port bases; callers must know when to add per-block offsets.
- Field constructors do not mask input values, so callers must validate ranges before using `V_*` macros.
- Hardware side effects are not visible in this header. Callers must know which registers are clear-on-read, write-one-to-clear, busy-waited, or reset-sensitive.
- Updating this file for a new chip revision risks breaking older revisions because many bits are revision-specific but not encoded in the macro names.

## Test signals

Validation should include compile coverage for all users, hardware smoke tests for SGE queue setup, interrupt enable/cause handling, TP RSS/MTU/offload setup, MC5 initialization, XGM link transitions, ethtool register dumps, and fault injection for parity/error bits. Static checks can compare `A_*` offsets and `S_/M_/V_/G_` fields against vendor register specifications and assert that value constructors are only fed bounded inputs.
