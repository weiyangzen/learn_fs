# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc4_cfg_regs.h

## Purpose

This auto-generated GPL-2.0 header defines the Gaudi TPC4 configuration register offsets for direct MMIO access. It is included through `include/gaudi/asic_reg/gaudi_regs.h`, which lets Gaudi driver code use symbolic `mmTPC4_CFG_*` names instead of hard-coded offsets. The file contains 602 register macros from `mmTPC4_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xF06400` through `mmTPC4_CFG_QM_SRF_31` at `0xF06E3C`.

## Important APIs, types, and macros

The file exports only preprocessor macros; it declares no C functions, structs, enums, or storage. The major macro families are:

- `mmTPC4_CFG_KERNEL_TENSOR_0..15_*`: 16 tensor descriptor blocks, each with base address low/high, padding value, tensor configuration, and five dimension size/stride pairs.
- `mmTPC4_CFG_KERNEL_*`: kernel sync object, kernel code base, five TID base/size pairs, kernel configuration/id, and `KERNEL_SRF_0..31` scalar register fields.
- `mmTPC4_CFG_*` control/status registers: `ROUND_CSR`, `PROT`, `SEMAPHORE`, `VFLAGS`, `SFLAGS`, `LFSR_POLYNOM`, `STATUS`, base/subtract address controls, `TPC_CMD`, `TPC_EXECUTE`, `TPC_STALL`, icache base registers, read/write rate limits, interrupt cause/mask, ARUSER/AWUSER, LUT function base registers, TSB/debug-memory controls, WQ/TSB counters, and MBIST controls.
- `mmTPC4_CFG_QM_TENSOR_0..15_*` and `mmTPC4_CFG_QM_*`: a second tensor/kernel/SRF register image used by the queue-manager side of the TPC configuration aperture.

## Control flow and state behavior

There is no executable control flow in the header. Runtime behavior appears where driver code writes these offsets through register helpers such as `WREG32`. Observed integration includes `gaudi_tpc_stall()` writing `mmTPC4_CFG_TPC_STALL`, `gaudi_mmu_prepare_reg()` programming `mmTPC4_CFG_ARUSER_LO` and `mmTPC4_CFG_AWUSER_LO` with an ASID, and security setup deriving protection-bit masks from TPC4 CFG offsets. The registers represent hardware state, not kernel-owned persistent data; values survive according to device reset and power behavior, while the macros themselves are compile-time constants.

## Dependencies and integration points

The header is guarded by `ASIC_REG_TPC4_CFG_REGS_H_` and is pulled into the Gaudi register aggregate. It aligns with `gaudi_blocks.h`, where `mmTPC4_CFG_BASE` is `0x7FFCF06000ull` and the CFG sub-block bases start at the same low offsets represented here. Bitfield shifts and masks are not defined in this file; driver users combine these offsets with TPC0-compatible field definitions such as `TPC0_CFG_TPC_STALL_V_SHIFT`.

## Risks and test signals

Because the file is generated and hardware-facing, manual edits are high risk: a wrong address can stall, misconfigure, or expose the wrong TPC engine. Macro spelling quirks such as `ICACHE_BASE_ADDERESS_*` and `IRQ_OCCOUPY_CNTR` are part of the generated API and should not be "fixed" locally without regenerating all dependent headers. Useful validation signals are build coverage of Gaudi register users, static checks that TPC4/5/6 normalized CFG layouts remain identical except for base address, reset tests that stop/stall TPCs, MMU ASID programming tests, and security/protection-bit tests that depend on address-to-bit calculations.
