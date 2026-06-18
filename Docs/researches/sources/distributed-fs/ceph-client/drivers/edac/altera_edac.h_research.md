# sources/distributed-fs/ceph-client/drivers/edac/altera_edac.h Research

## Purpose
This header is the register-map and private-data contract for `altera_edac.c`. It centralizes SDRAM, ECC-manager, OCRAM, L2, Arria10, Stratix10, and peripheral ECC offsets, bit masks, injection constants, and driver-private structures.

## Important APIs, Types, and Functions
The header defines register offsets and masks such as `CV_CTLCFG_ECC_EN`, `A10_ECCCTRL1_ECC_EN`, `ALTR_A10_ECC_*`, `A10_SYSMGR_ECC_INTMASK_*`, `ALTR_S10_ECC_*`, sticky S10 UE registers, and ECC block transaction registers. `struct altr_sdram_prv_data` describes SDRAM register layout and injection controls. `struct altr_sdram_mc_data` holds the SDRAM regmap, IRQs, and layout pointer. `struct edac_device_prv_data` describes per-device setup, clear masks, allocation hooks, injection hooks, and panic policy. `struct altr_edac_device_dev` is per-child EDAC device state. `struct altr_arria10_edac` is the top-level ECC-manager state with regmap, IRQ domain, IRQ chip, child list, and panic notifier.

## Control Flow
The header has no executable flow. Its data structures drive `altera_edac.c`: match tables select an `edac_device_prv_data` or `altr_sdram_prv_data`, probe code uses the offsets and masks to validate/enable ECC, IRQ handlers use clear/status masks, and debugfs injection uses allocation and file-operation callbacks.

## State and Persistence
No state is allocated in the header. It defines the shapes of runtime state allocated by the C file and the constants used to read or mutate persistent hardware ECC state in memory-controller and system-manager registers.

## Dependencies and Integration Points
It includes `linux/arm-smccc.h`, `linux/edac.h`, and `linux/types.h`, and forward-declares internal driver structures. It is tightly coupled to Intel/Altera SoCFPGA device-tree bindings and register manuals. The structures are not exported as a generic subsystem API; they are private to the Altera EDAC implementation.

## Risks and Edge Cases
Incorrect offsets or bit masks can cause missed interrupts, unwanted ECC disable/enable, or writes to unrelated system-manager fields. Some physical addresses are hardcoded for older SDRAM interface registers, so SoC-specific use must match the documented platform. Repeated generic field names for Cyclone5 and Arria10 variants make accidental table mixups possible.

## Test Signals
Compile tests catch structure and macro drift against `altera_edac.c`. Runtime validation requires reading known ECC registers on supported SoCFPGA hardware, confirming match-table data writes the intended bits, and exercising debug injection and IRQ clear paths for each enabled device type.
