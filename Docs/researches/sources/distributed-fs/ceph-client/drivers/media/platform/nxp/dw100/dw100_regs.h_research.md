# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/dw100/dw100_regs.h

Purpose: Register map and bitfield helper macros for the DW100 dewarper hardware.

Important APIs, types, and functions: Defines offsets for control, LUT address/size, source/destination image bases/sizes/strides, swap control, split lines, scale, ROI, boundary pixel, interrupt status, bus control, timeout, and destination plane sizes. Macros such as `DW100_DEWARP_CTRL_INPUT_FORMAT()`, `DW100_MAP_LUT_ADDR_ADDR()`, `DW100_IMG_SIZE_WIDTH()`, `DW100_SWAP_CONTROL_*()`, `DW100_INTERRUPT_STATUS_INT_*`, and `DW100_BUS_CTRL_AXI_MASTER_ENABLE` encode register fields.

Control flow: No runtime control flow. `dw100.c` consumes these macros while programming the hardware before each job, handling IRQ status, clearing interrupts, and enabling/disabling the AXI master.

State and persistence behavior: No software state. The definitions represent hardware state layout that persists in device registers while powered.

Dependencies and integration points: Requires Linux bit macros (`BIT`, `GENMASK`) through including code. It is tightly coupled to the DW100 MMIO programming sequence in `dw100.c`.

Risks: Field macros shift DMA addresses by 4 and mask to 30 bits, so address alignment and addressable range are implicit requirements. Incorrect masks or swapped source/destination fields would cause image corruption or bus faults. Interrupt status combines status, enable, busy, and clear fields in one register, increasing risk of write-side mistakes.

Test signals: Register dumps before/after a job should match expected source/destination geometry, LUT, swap, and interrupt bits. Static compile tests catch macro syntax, while hardware tests with each supported pixel format catch format/swap field errors.
