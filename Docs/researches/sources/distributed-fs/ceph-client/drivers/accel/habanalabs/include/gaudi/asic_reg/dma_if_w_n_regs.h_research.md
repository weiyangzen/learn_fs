# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma_if_w_n_regs.h

## Purpose

`dma_if_w_n_regs.h` is the auto-generated register address map for the top-level Gaudi west/north DMA interface block, `DMA_IF_W_N`. It covers HBM credit controls, low-bandwidth protection range registers for SOB/DMA initiators, hit/status registers, and miscellaneous bin/I2C/misc controls. The file exports 419 macro constants in the `mmDMA_IF_W_N_*` namespace. The address window starts at `mmDMA_IF_W_N_HBM0_WR_CRED_CNT` (`0x4C0000`) and ends at `mmDMA_IF_W_N_HBM_MISC` (`0x4C0834`).

## Important APIs, Types, And Register Families

There are no functions, data structures, or inline APIs. The public interface is the macro set:

- `HBM0_WR_CRED_CNT`, `HBM1_WR_CRED_CNT`, `HBM0_RD_CRED_CNT`, and `HBM1_RD_CRED_CNT`: programmed by `gaudi_init_hbm_cred()` with per-HBM read/write credit patterns.
- `HBM_LIMITER_0..3`, `HBM_ALMOST_EN_0..1`, and `HBM_CRED_EN_0..1`: HBM credit and limiter controls; the enable registers are written after credit counts.
- `SOB_*`, `DMA0_*`, and `DMA1_*` range tables: 16-entry low-bandwidth minimum/maximum windows for read/write protection (`RPROT`, `WPROT`) and read/write privilege (`RPRIV`, `WPRIV`).
- `SOB_HIT_*`, `DMA0_HIT_*`, and `DMA1_HIT_*`: hit/status registers for protection or privilege violations.
- `HBM_BIN`, `MME_BIN`, `TPC_BIN`, `DMA_BIN`, and `SOB_CG_EN`: miscellaneous binning/clock-gate style controls.
- `HBM_I2C_ADDR_0..4` and `HBM_MISC`: HBM sideband address and miscellaneous control registers.

## Control Flow

The header itself is declarative. In driver control flow:

- `gaudi_init_hbm_cred()` writes the four HBM credit count registers for west/north, then enables read/write HBM credits through `HBM_CRED_EN_0` and `HBM_CRED_EN_1` if firmware has not already done so.
- `gaudi_security.c` includes the `SOB`, `DMA0`, and `DMA1` low-bandwidth hit/min/max registers in arrays that program or inspect low-bandwidth protected ranges. The arrays depend on the `_0` entry as the base of each 16-register table.
- `gaudi_coresight.c` uses related W/N DMA interface block bases from `gaudi_blocks.h` for tracing/monitoring integration, while this header provides the functional block's register offsets.

## State And Persistence Behavior

The header has no software state. It names persistent hardware registers. HBM credit programming persists until reset or reconfiguration. Low-bandwidth protection windows and hit registers represent device security state; hits may be latched or inspected by security paths depending on the hardware behavior encoded outside this header. Driver writes are conditional on firmware security ownership and boot status bits such as `CPU_BOOT_DEV_STS0_HBM_CRED_EN`.

## Dependencies

Compile-time dependency is inclusion by `gaudi_regs.h`. Runtime dependencies include `WREG32`, HBM credit bit shifts such as `DMA_IF_HBM_CRED_EN_READ_CREDIT_EN_SHIFT` and `DMA_IF_HBM_CRED_EN_WRITE_CREDIT_EN_SHIFT`, and the security code's range-register programming helpers. The low-bandwidth tables depend on generated contiguity: each of SOB, DMA0, and DMA1 has repeated 16-entry min/max tables for read/write protection and privilege.

## Integration Points

This header integrates with:

- `gaudi.c` golden-register initialization for HBM credit count and enable registers.
- `gaudi_security.c` low-bandwidth protection arrays for SOB/DMA0/DMA1 ranges and hit status.
- `gaudi_regs.h`, which aggregates generated register headers for the Gaudi driver.
- `gaudi_blocks.h`, whose `mmDMA_IF_W_N_BASE` identifies the block base used by protected-block logic and tracing infrastructure.

## Risks

The highest risk is security range misprogramming. The low-bandwidth protection arrays in `gaudi_security.c` assume the generated min/max tables are ordered consistently and can be addressed from `_0`. A single wrong offset can produce a security hole or false violation. HBM credit registers affect traffic flow; wrong credit values or enable registers can throttle, deadlock, or overload the memory path. Because this is macro-only generated code, compiler type checking cannot distinguish a protection register from a credit register.

## Test Signals

Good test signals include successful Gaudi driver compilation, boot tests that run `gaudi_init_hbm_cred()`, security tests that configure SOB/DMA low-bandwidth protection ranges, and negative tests that intentionally trigger read/write protection hits and observe the `*_HIT_*` registers. Generator validation should compare this file with the authoritative ASIC register database and with the south-side sibling for expected `0x40000` north/south address separation.
