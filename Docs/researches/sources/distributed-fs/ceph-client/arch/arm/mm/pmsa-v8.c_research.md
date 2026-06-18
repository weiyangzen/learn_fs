# sources/distributed-fs/ceph-client/arch/arm/mm/pmsa-v8.c

## Purpose
This file programs ARM PMSAv8 MPU regions for no-MMU systems. It builds RAM and I/O ranges around early fixed kernel/XIP/vector regions and programs PRBAR/PRLAR pairs with normal or device memory attributes.

## Important APIs, Types, and Functions
Static `struct range` arrays `io[]` and `mem[]` hold planned regions. `is_region_fixed()` protects `PMSAv8_XIP_REGION` and `PMSAv8_KERNEL_REGION`. `pmsav8_adjust_lowmem_bounds()` keeps only the first RAM bank contiguous from `PHYS_OFFSET`. `__mpu_max_regions()` reads MPUIR once. `__pmsav8_setup_region()` writes `PRSEL`, `PRBAR`, and `PRLAR` and records values in `mpu_rgn_info`. `pmsav8_setup_ram()`, `pmsav8_setup_io()`, `pmsav8_setup_fixed()`, and `pmsav8_setup_vector()` build region attributes.

## Control Flow
Boot first adjusts memblock to one contiguous RAM bank. Setup then creates a RAM range from the first memblock memory region and an I/O range covering 4 GB. It subtracts kernel, optional XIP, vectors, and RAM from the relevant ranges. It verifies fixed early regions, then programs I/O ranges, RAM ranges, and vectors sequentially. Errors produce a warning rather than a panic.

## State and Persistence Behavior
The file stores planned ranges only in `__initdata`, records final MPU register pairs in `mpu_rgn_info`, and writes persistent hardware MPU state. It mutates memblock by discarding later RAM ranges.

## Dependencies and Integration Points
It is selected from `nommu.c` through `MMFR0.PMSA`. It depends on memblock, generic `range` add/subtract helpers, ARM CP15 or V7-M SCB register accessors, XIP/kernel section symbols, `vectors_base`, and PMSAv8 attribute constants.

## Risks
Region pressure is high because a full 4 GB I/O cover is split by exclusions. If the hardware supports too few regions, setup can fail and only warn, leaving mappings incomplete. Fixed-region verification assumes early assembly programmed kernel/XIP entries exactly. Attribute mistakes can expose executable device memory or non-cacheable RAM.

## Test Signals
Boot PMSAv8 no-MMU targets with and without XIP, with vectors enabled on non-V7-M systems, and with limited MPU region counts. Inspect log messages, `mpu_rgn_info`, and region register dumps. Exercise RAM access, device MMIO, vector faults, and secondary/resume paths that reuse recorded MPU state.
