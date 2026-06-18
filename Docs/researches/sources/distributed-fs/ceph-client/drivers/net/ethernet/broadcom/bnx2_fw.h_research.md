# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2_fw.h

## Purpose
`bnx2_fw.h` is a small firmware-support header for the older Broadcom/QLogic `bnx2` Ethernet driver. It defines static `struct cpu_reg` initializer tables for the on-chip microcontrollers used by the device firmware loader and reset paths. The file does not contain executable logic; it binds symbolic register constants from the bnx2 register definitions into per-processor register layouts consumed elsewhere by the driver.

## Important APIs, Types, and Data
- `cpu_reg_com` describes the Completion Processor register block: mode, halt/step values, state, GPR base, event mask, program counter, instruction, breakpoint, scratchpad base, and MIPS view base.
- `cpu_reg_cp` describes the Command Processor with the same `struct cpu_reg` fields mapped to `BNX2_CP_*` registers.
- `cpu_reg_rxp` describes the RX Processor register block.
- `cpu_reg_tpat` describes the TX Patch-up Processor register block.
- `cpu_reg_txp` describes the TX Processor register block.
- All tables use `.mips_view_base = 0x8000000`, so consumers can treat the firmware CPU memory window consistently across these processors.

## Control Flow
There is no local control flow. The driver code that halts, steps, clears state, reads/writes GPRs, loads firmware, or dumps microcontroller state selects one of these constant structures and performs MMIO against the addresses embedded here.

## State and Persistence Behavior
The constants are compile-time `static const` data. They do not mutate driver state and do not persist anything. The runtime state affected by their consumers is hardware state: firmware CPU mode/state registers, scratchpad memory, event masks, program counters, and instruction/breakpoint registers.

## Dependencies and Integration Points
- Depends on `struct cpu_reg` and the `BNX2_*` register macros being defined before inclusion.
- Integrates with the bnx2 firmware initialization and diagnostic paths that need a uniform description of the COM, CP, RXP, TPAT, and TXP processor register blocks.
- The register addresses must match the firmware image and the silicon generation expected by the bnx2 driver.

## Risks
- Incorrect register mappings can halt or program the wrong microcontroller block, causing device initialization failures or corrupting firmware execution.
- Since the file is pure static data, compile-time type checking is limited to field names and scalar values; semantic mistakes surface only during hardware bring-up or firmware diagnostics.
- Changes must be synchronized with the corresponding bnx2 register header and firmware loader code.

## Test Signals
- Driver probe/load succeeds on bnx2 hardware and firmware CPUs leave soft-halt/reset as expected.
- Firmware reload, reset, and diagnostic dump paths read coherent program counter/state values for each processor.
- Build coverage catches missing `struct cpu_reg` fields or renamed `BNX2_*` constants.
