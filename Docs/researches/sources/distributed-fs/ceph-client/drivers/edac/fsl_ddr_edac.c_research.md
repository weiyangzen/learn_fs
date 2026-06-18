# sources/distributed-fs/ceph-client/drivers/edac/fsl_ddr_edac.c

## Purpose
This platform EDAC driver supports Freescale/NXP DDR memory controllers on Power-based and Layerscape/i.MX platforms. It maps controller registers, validates ECC enablement, describes chip-select rows, reports correctable and uncorrectable ECC events, and optionally exposes debug error-injection sysfs attributes.

## Important APIs and Functions
`ddr_reg_addr()`, `ddr_in32()`, and `ddr_out32()` abstract endianness and i.MX9 register layout differences. Debug attributes expose injection data/control registers. `calculate_ecc()`, `syndrome_from_bit()`, and `sbe_ecc_decode()` diagnose single-bit errors on 64-bit data. `fsl_mc_check()` is the polling/IRQ error processor. `fsl_mc_isr()` handles interrupt mode. `fsl_ddr_init_csrows()` populates EDAC DIMM metadata. `fsl_mc_err_probe()` and `fsl_mc_err_remove()` are the platform lifecycle hooks.

## Control Flow
Probe allocates a two-layer EDAC memory controller, reads device-tree match flags and endianness, maps the main register resource and optional i.MX9 injection resource, verifies ECC enablement, sets EDAC capabilities, initializes chip-select rows, clears/reenables error detection, registers with EDAC, and optionally enables IRQ mode. Checks read `ERR_DETECT`, ignore non-ECC bits after clearing, capture syndrome/address/data, locate the csrow by PFN, report CE/UE via `edac_mc_handle_error()`, then clear detected bits.

## State and Persistence
Per-device state is `struct fsl_mc_pdata`: mapped bases, IRQ, saved error-disable/SBE-threshold registers, endianness, and variant flag. Hardware register state is modified while the driver is active and restored on remove.

## Dependencies and Integration
The driver depends on device tree resources/properties, platform IRQs, MMIO accessors, EDAC core memory-controller APIs, and `fsl_ddr_edac.h` register definitions.

## Risks
Register layout differs for i.MX9, so offsets must remain synchronized with hardware manuals. `orig_ddr_err_sbe` is saved only in interrupt mode but restored unconditionally, which should be reviewed for poll-mode behavior. Single-bit decode explicitly lacks 32-bit bus support.

## Test Signals
Useful signals are successful probe only when ECC is enabled, accurate DIMM pages/types in EDAC sysfs, CE/UE reports from hardware or debug injection, IRQ handling in interrupt mode, and restoration of error mask/threshold registers on remove.
