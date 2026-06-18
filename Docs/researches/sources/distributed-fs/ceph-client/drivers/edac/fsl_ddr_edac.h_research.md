# sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.h

## Purpose
This header provides Freescale DDR EDAC register offsets, bit definitions, private per-controller state, and probe/remove declarations shared by the platform glue and the main FSL DDR EDAC implementation.

## Important APIs and Types
`fsl_mc_printk()` wraps EDAC chipset logging. Register constants cover SDRAM configuration, chip-select bounds, error injection, capture registers, error detect/disable/interrupt enable, captured address, SBE threshold, and i.MX9-specific error-enable/injection offsets. Bit definitions describe memory/ECC enablement, bus width, registered-DIMM mode, memory type, interrupt-enable bits, error-detect bits, and error-disable bits. `struct fsl_mc_pdata` stores MMIO bases, IRQ, saved registers, endianness, and variant flag.

## Control Flow
The header has no runtime flow; `fsl_ddr_edac.c` consumes the constants to decide whether ECC is enabled, which MMIO base to use, how to decode chip-select ranges, and what to restore on removal.

## State and Persistence
The only state definition is `struct fsl_mc_pdata`, which persists for the lifetime of the EDAC memory-controller allocation. It mirrors controller configuration and mutable hardware settings that must be restored later.

## Dependencies and Integration
The header expects platform-device context for `fsl_mc_err_probe()` and `fsl_mc_err_remove()`, and it is tightly coupled to the EDAC memory-controller private data in the C file. It encodes both legacy FSL and i.MX9 register maps.

## Risks
Offsets and masks are hardware contracts. Incorrect values can cause MMIO writes to the wrong control register, especially because i.MX9 remaps injection/error-enable ranges. The `TYPE_IMX9` flag is a simple numeric match-data bit, so future variants need clear flag allocation.

## Test Signals
Compile-time users should include this header without conflicting register names. Runtime validation comes from correct ECC enable detection, proper endianness behavior, correct error capture decoding, and successful i.MX9 versus non-i.MX9 register addressing.
