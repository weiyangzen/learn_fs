# sources/distributed-fs/ceph-client/include/linux/jz4780-nemc.h

## Purpose
Declares the shared API for the Ingenic JZ4780 NAND/external memory controller. It lets child drivers query banks, set a bank type, and assert or deassert a bank.

## Important APIs, Types, And Functions
`JZ4780_NEMC_NUM_BANKS` is defined as 7 because hardware bank numbers start at 1. `enum jz4780_nemc_bank_type` distinguishes SRAM and NAND banks. Exported functions are `jz4780_nemc_num_banks()`, `jz4780_nemc_set_type()`, and `jz4780_nemc_assert()`.

## Control Flow
Child drivers obtain the controller device, query supported bank count, configure a bank type, and assert/deassert bank selection as needed. The header itself has no inline logic.

## State And Persistence
State is stored in NEMC hardware registers and controller driver state. It persists until reconfigured or reset.

## Dependencies And Integration Points
Depends on `linux/types.h` and `struct device`. Integrates with NAND, SRAM, and board/SoC glue drivers that share the memory controller.

## Risks
Bank numbering can cause off-by-one errors because bank zero is not a real hardware bank. Incorrect type or assert sequencing can break attached memory devices. The implementation must serialize shared controller register updates.

## Test Signals
Signals include boot probing on JZ4780 boards, bank-count validation, NAND and SRAM access tests, invalid bank handling, and suspend/resume register restoration.
