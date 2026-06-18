# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc5_cfg_regs.h

## Purpose

This auto-generated header is the TPC5 instance of the Gaudi TPC configuration register map. It has the same normalized macro layout as the TPC4 and TPC6 CFG headers, but all exported names use the `mmTPC5_CFG_*` prefix and addresses are in the TPC5 CFG aperture. The file contains 602 macros from `mmTPC5_CFG_KERNEL_TENSOR_0_BASE_ADDR_LOW` at `0xF46400` through `mmTPC5_CFG_QM_SRF_31` at `0xF46E3C`.

## Important APIs, types, and macros

No functions, types, or variables are defined; the public surface is register macros. The important groups are the 16 `KERNEL_TENSOR_*` descriptors, kernel sync/code/TID/config/id/SRF registers, central TPC CFG control and status registers, ARUSER/AWUSER registers, LUT and debug-memory controls, WQ/TSB counters, MBIST controls, and the mirrored `QM_TENSOR_*` plus `QM_*` tensor/kernel/SRF image.

## Control flow and state behavior

Control flow is entirely in consumers. `gaudi_tpc_stall()` writes `mmTPC5_CFG_TPC_STALL`; MMU setup prepares `mmTPC5_CFG_ARUSER_LO` and `mmTPC5_CFG_AWUSER_LO`; security code computes protection-bit masks from TPC5 CFG register offsets. The constants describe MMIO state for one TPC engine. The kernel does not persist anything in this header; register contents are device state and are reset/reinitialized by Gaudi bring-up and reset paths.

## Dependencies and integration points

The header is included by `gaudi_regs.h` and corresponds to `mmTPC5_CFG_BASE` in `gaudi_blocks.h` (`0x7FFCF46000ull`). Its layout matched the TPC4/TPC6 CFG normalized macro sequence during review, which allows common driver routines to use TPC0-compatible bitfield definitions against per-instance addresses.

## Risks and test signals

Generated-address drift is the main risk. TPC5 offsets are separated from TPC4 and TPC6 by aperture placement, not by semantic layout, so any hand edit can silently desynchronize multi-TPC reset, MMU, or security logic. Tests should build Gaudi register consumers, exercise TPC5 stall/reset and queue launch paths, verify MMU ASID propagation to CFG ARUSER/AWUSER, and compare normalized TPC4/TPC5/TPC6 CFG macro order and count.
