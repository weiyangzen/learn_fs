# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_security.c

## Purpose

`goya_security.c` programs the Goya ASIC security model during device bring-up. It configures two related mechanisms: address-range protection for DMA/MME/TPC routing paths, and per-register protection bits inside 4 KiB configuration-register blocks. The exported entry point is `goya_init_security()`, which writes low-bandwidth and high-bandwidth range filters, then calls the protection-bit initializers. `goya_ack_protection_bits_errors()` exists as an exported hook but is currently empty.

## Important APIs, Types, and Functions

The file depends on `struct hl_device` and `struct goya_device` from the HabanaLabs driver, register definitions from `goya_regs.h`, and MMIO helpers/macros such as `WREG32`, `lower_32_bits`, `upper_32_bits`, `CFG_BASE`, `DRAM_PHYS_BASE`, `PROT_BITS_OFFS`, and `DMA_MACRO_LBW_RANGE_BASE_R_MASK`.

`goya_pb_set_block()` computes the protection-bit shadow address for a register block from `base - CFG_BASE + PROT_BITS_OFFS` and writes zeroes through the protection-bit area until the address reaches a 4 KiB boundary. In this hardware model, a protection bit value of zero marks the corresponding register as protected.

`goya_init_mme_protection_bits()`, `goya_init_dma_protection_bits()`, and `goya_init_tpc_protection_bits()` carve out large lists of MME, DMA, and TPC registers. They protect whole routing/regulator/memory blocks using `goya_pb_set_block()`, then compute word offsets and bit masks for selected registers such as queue-manager globals, PQ/CQ descriptors, CP message base registers, debug-memory registers, semaphore/status/config registers, ARUSER/AWUSER controls, and interrupt mask/status registers.

`goya_init_protection_bits()` is the top-level per-register protection setup. It protects PCIe, SRAM banks, PCIe subblocks, TPC PLL, MME, DMA, and TPC areas, and documents the bit layout used to map a register address to a protection-bit word and bit.

`goya_init_security()` programs range-protection registers for the DMA macro, MMEs, and TPC routers. It defines 14 low-bandwidth register ranges and high-bandwidth host/DDR ranges, taking `HW_CAP_MMU` into account for DMA host protection.

## Control Flow

Initialization starts in `goya_init_security()`. It derives DRAM low/high address words from `DRAM_PHYS_BASE` and masks each hard-coded LBW range through `DMA_MACRO_LBW_RANGE_BASE_R_MASK`. It first enables range-hit blocking on DMA macro LBW/HBW paths. If the MMU capability is not initialized, DMA HBW range 0 is used to protect host space; range 1 protects the first 512 MiB of DDR. It then writes all LBW range base/mask pairs into the DMA macro.

The same host/DDR/LBW range pattern is repeated for MME router blocks 1 through 6 and TPC router blocks 0 through 7. Each engine gets LBW hit blocking (`0xFFFF`) and HBW hit blocking (`0xFE`) plus host range 0, DDR range 1, and all 14 LBW ranges. After range setup, `goya_init_security()` calls `goya_init_protection_bits()`, which dispatches to the MME, DMA, and TPC protection-bit helpers.

The protection-bit helpers are mostly straight-line MMIO writes. For individual allow-list words, the code computes `pb_addr = (reg & ~0xFFF) + PROT_BITS_OFFS`, `word_offset = ((reg & PROT_BITS_OFFS) >> 7) << 2`, and `mask = 1 << ((reg & 0x7F) >> 2)` for each register in the same protection word. It then writes `~mask`, meaning the selected registers remain unprotected while other bits in that word are protected. Whole-block protection writes zeroes over the block's protection-bit tail.

## State and Persistence Behavior

There is no heap allocation, persisted kernel state, or software data structure mutation beyond reading `goya->hw_cap_initialized`. The meaningful state is hardware state in memory-mapped registers. Once written, the range and protection-bit registers persist in the device until reset or later reprogramming. Because most writes are one-way configuration during initialization, ordering matters: later protection-bit writes can make future software access to some registers impossible unless the intended allow-list is correct.

## Dependencies and Integration Points

This file integrates with Goya ASIC initialization through the exported `goya_init_security()` symbol, and it assumes the register map in `include/goya/asic_reg/goya_regs.h` matches the silicon. It also depends on common HabanaLabs device capability tracking: if `HW_CAP_MMU` is absent, DMA host protection is programmed explicitly; otherwise the MMU path is expected to provide the host isolation. The range values also integrate with the driver's DRAM base model and with firmware/security settings that define accessible host and device address windows.

## Risks

The highest risk is stale or incorrect register constants. A wrong address, mask, or engine copy-paste entry can either expose privileged registers or block a register required for normal initialization, queue operation, interrupt handling, debug, or error recovery. The repeated MME/TPC/DMA blocks are difficult to audit and easy to drift across engines. The inverted protection-bit writes are also subtle: a mistaken mask polarity changes the security meaning. `goya_pb_set_block()` relies on block-aligned assumptions and the protection-bit tail layout; if `base` is outside the expected CFG window or the hardware layout changes, it can write unintended registers. `goya_ack_protection_bits_errors()` being empty means there is no visible recovery path here for protection-bit fault acknowledgement.

## Test Signals

Useful validation signals include successful device probe after `goya_init_security()`, working DMA/MME/TPC queue bring-up, no unexpected RAZWI/security faults during normal workloads, and expected faults when protected host/register/DDR ranges are accessed by unauthorized engines. Hardware or simulator tests should read back representative range registers and protection-bit words, especially for each repeated MME/TPC/DMA engine. Regression tests should cover both MMU-enabled and MMU-disabled initialization paths, and should include negative tests for register access that should be blocked after protection-bit programming.
