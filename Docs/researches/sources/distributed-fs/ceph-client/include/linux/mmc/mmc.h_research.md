# sources/distributed-fs/ceph-client/include/linux/mmc/mmc.h

## Purpose
`mmc/mmc.h` is the protocol constant header for native MMC/eMMC commands, status bits, command classes, CSD/EXT_CSD field offsets, EXT_CSD field values, card type capability bits, bus width/timing values, power notification values, command queue bits, switch modes, and erase/trim arguments.

## Important APIs, Types, And Functions
The header defines command opcodes such as `MMC_GO_IDLE_STATE`, `MMC_SEND_OP_COND`, `MMC_SWITCH`, `MMC_SEND_EXT_CSD`, read/write/erase commands, tuning commands, application commands, and command-queue task commands. Inline helpers `mmc_op_multi()`, `mmc_op_tuning()`, and `mmc_ready_for_data()` classify commands/status. Status macros include R1 native error/state bits, SPI R1/R2 bits, OCR busy, CCC capabilities, CSD versions, EXT_CSD offsets, HS/DDR/HS200/HS400 card type bits, bus width/strobe values, secure erase bits, BKOPS bits, CMDQ bits, and `mmc_driver_type_mask()`.

## Control Flow And State
No state is stored here. Control flow is encoded through constants consumed by MMC command construction and response parsing. For example, block code selects multiblock or tuning behavior with `mmc_op_multi()`/`mmc_op_tuning()`, polling code uses `mmc_ready_for_data()` to require both ready and TRAN state, and switch logic builds `MMC_SWITCH` arguments from access mode, EXT_CSD byte, value, and command set.

## Dependencies And Integration Points
The file depends on Linux integer types and integrates with `core.h` command structures, `card.h` EXT_CSD parsing, host tuning, block erase/trim/discard, eMMC partitioning, power-off notification, BKOPS, HPI, HS200/HS400 setup, and command queue support.

## Risks And Test Signals
Risks include opcode/field offset drift against eMMC specs, status-bit misinterpretation, incorrect ready polling for broken cards, unsafe secure erase/trim argument use, and capability bits that do not match parsed EXT_CSD revision. Test signals include EXT_CSD parser tests, status decode tests, switch-mode tests, multiblock/tuning command tests, erase/trim/discard integration tests, and conformance checks against known card register dumps.
