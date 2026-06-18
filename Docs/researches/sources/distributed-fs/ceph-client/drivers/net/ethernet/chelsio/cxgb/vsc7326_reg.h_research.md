# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/vsc7326_reg.h

## Purpose
`vsc7326_reg.h` defines the register address map for the Vitesse VSC7321/VSC7326 MAC used by the `vsc7326.c` driver. It provides the `CRA` encoder plus symbolic names for system, aggregator, BIST, FIFO, SPI4, 10GbE, tri-speed MAC, statistics, MIIM, and ingress filter registers.

## Important APIs, Types, And Functions
- `CRA(blk, sub, adr)` composes the VSC register address from block, sub-block, and register fields.
- System/CPU communication registers include chip ID, reset, memory BIST, interface mode, PLL/sys clocks, GPIO, local data, and local status.
- FIFO macros parameterize ingress/egress and FIFO number: `REG_TEST`, `REG_TOP_BOTTOM`, `REG_HIGH_LOW_WM`, `REG_CT_THRHLD`, `REG_CONTROL`, and related SRAM/debug registers.
- SPI4 registers cover setup, status, deskew, pattern generator/checker, sticky, debug, and grant/status values.
- MAC registers cover 10GbE-specific state and tri-speed per-port registers such as `REG_MODE_CFG`, `REG_PAUSE_CFG`, `REG_MAX_LEN`, `REG_MAC_HIGH_ADDR`, `REG_MAC_LOW_ADDR`, `REG_DEV_SETUP`, `REG_DBG`, and `REG_TX_IFG`.
- The statistics enum names RMON counter indices used by `vsc7326.c`, with helper macros for byte counters.
- Ingress filter macros include unicast/multicast enable, values, masks, and ethertype registers.

## Control Flow And State
The header has no executable flow. Its state model is the VSC register layout. `vsc7326.c` uses these macros to build initialization tables, reset ports, update watermarks, configure MAC addresses and filters, read RMON counters, and clear statistics.

## Dependencies And Integration Points
It is tightly coupled to `vsc7326.c` and to `gmac` operations for VSC-based boards. It also indirectly depends on TPI access because the VSC driver converts these CRA addresses to TPI offsets for 16-bit high/low register accesses.

## Risks And Edge Cases
`CRA` accepts raw values and masks them, so invalid block/sub/address values silently alias rather than failing. Several comments note datasheet quirks and errata, especially MIIM and traffic shaper encoding. The header includes registers that are not used, which can be useful for diagnostics but increases the chance of selecting a plausible but wrong register.

## Test Signals
Static build coverage confirms macro names. Runtime validation comes through VSC MAC tests: reset/BIST, port initialization, SPI4 datapath lock, MAC address filter behavior, stats counter reads, and speed/flow-control programming.
