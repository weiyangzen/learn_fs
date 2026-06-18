# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_regs.h

## Purpose
This header provides CN68XX-specific register definitions that supplement the mostly shared CN66XX/CN6XXX register map.

## Important APIs, Types, And Functions
It defines `CN68XX_SLI_IQ_PORT0_PKIND`, `CN68XX_SLI_IQ_PORT_PKIND(iq)`, `CN68XX_SLI_TX_PIPE`, and `CN68XX_INTR_PIPE_ERR`. `CN68XX_SLI_IQ_PORT_PKIND()` uses `CN6XXX_IQ_OFFSET`, so it is meant to be used with the common CN6XXX register header.

## Control Flow
There is no executable logic. The CN68XX setup implementation uses `CN68XX_SLI_TX_PIPE` to program output pipe count. Other macros are available for PKIND and pipe-error handling.

## State And Persistence
State is hardware register state only. The header does not allocate or persist anything.

## Dependencies And Integration Points
It depends on `CN6XXX_IQ_OFFSET` and kernel bit macros being available from surrounding includes. It extends CN66XX/CN6XXX register definitions for CN68XX-specific hardware blocks.

## Risks
Because the header relies on definitions from another header, include ordering matters unless translation units already include `cn66xx_regs.h`. `CN68XX_INTR_PIPE_ERR` is defined but not included in the common CN6XXX interrupt mask read here, so pipe-error handling may require explicit integration elsewhere.

## Test Signals
Compile CN68XX code with expected include order, validate `CN68XX_SLI_TX_PIPE` writes, and exercise or audit pipe-error interrupt handling if `CN68XX_INTR_PIPE_ERR` is expected to be surfaced.
