# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/elmer0.h

## Purpose
`elmer0.h` defines the register offsets and bitfields for the Elmer0 FPGA/bridge used by Chelsio T1/T2 adapters. It is a pure hardware contract header: code uses these constants to access board-version, PHY configuration, external interrupt, GPIO, and MI1 MDIO-management registers through TPI accesses.

## Important APIs, Types, and Functions
The file exports no functions. It defines Elmer0 flavor IDs, top-level registers such as `A_ELMER0_VERSION`, `A_ELMER0_PHY_CFG`, `A_ELMER0_INT_ENABLE`, `A_ELMER0_INT_CAUSE`, `A_ELMER0_GPI_CFG`, `A_ELMER0_GPI_STAT`, `A_ELMER0_GPO`, and per-port MI1 register groups from port 0 through port 3. It also defines standard Chelsio `S_`, `M_`, `V_`, `G_`, and `F_` bitfield helpers for MI1 configuration, register/PHY addressing, data, operation selection, address auto-increment, and busy state.

The GPIO bit constants `ELMER0_GP_BIT0` through `ELMER0_GP_BIT19` are used by PHY/MAC drivers to reset external chips, enable lasers, toggle activity LEDs, and route external interrupts. `MI1_OP_DIRECT_WRITE`, `MI1_OP_DIRECT_READ`, and indirect operation constants define MDIO command encodings.

## Control Flow
There is no executable control flow. Runtime users compose Elmer0 register addresses and bitfields, then call `t1_tpi_read()`, `t1_tpi_write()`, `__t1_tpi_read()`, or `__t1_tpi_write()` to reach the FPGA. Interrupt-enable paths set bits in `A_ELMER0_INT_ENABLE`; clear paths write `A_ELMER0_INT_CAUSE`; reset/LED/clock paths manipulate `A_ELMER0_GPO`; MDIO paths use per-port MI1 config/address/data/op registers and poll `F_MI1_OP_BUSY`.

## State and Persistence
The header defines access to board hardware state but owns no memory. The persistent state is the Elmer0 register contents in the adapter until reset or power cycle: GPIO output level, interrupt masks/causes, and MI1 configuration. Some PHY code caches selected GPIO state in `struct cphy`, but this header only defines the bits.

## Dependencies and Integration Points
`cxgb2.c` uses `A_ELMER0_GPO` for T1B clock programming. `mv88e1xxx.c`, `mv88x201x.c`, `my3126.c`, and `pm3393.c` use Elmer0 GPIO and interrupt registers for PHY/MAC reset, external interrupt routing, LED/laser control, and clearing interrupt causes. The MDIO/TPI helpers in other driver files rely on the MI1 field definitions here.

## Risks
Because these constants map physical hardware registers, incorrect offsets or bit positions can reset the wrong external chip, leave interrupts stuck, or break MDIO access. GPIO bits are reused for board-specific semantics, so callers must combine this header with board type checks. Busy-bit polling and interrupt cause semantics are easy to misuse because the header does not encode timing requirements or write-one-to-clear behavior.

## Test Signals
Signals include successful PHY MDIO reads/writes on all ports, external interrupt enable/disable/clear behavior, link interrupt delivery from Marvell PHYs, PM3393 reset through GPIO bit 0, 10G PHY reset/laser enable through GPIO bits used by `mv88x201x` and `my3126`, T1B clock switching through `cxgb2.c`, and no stuck Elmer0 interrupt causes after link flaps.
