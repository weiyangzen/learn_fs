<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 74 macros including `_ASM_RC32434_DDR_H_`, `DDR0_PHYS_ADDR`, `DDR_MASK`, `DDR0_BASE_MSK`, `DDR1_BASE_MSK`, `RC32434_DDR0_ATA_BIT`, `RC32434_DDR0_ATA_MSK`, `RC32434_DDR0_DBW_BIT`, `RC32434_DDR0_DBW_MSK`, `RC32434_DDR0_WR_BIT`, `RC32434_DDR0_WR_MSK`, `RC32434_DDR0_PS_BIT`, `RC32434_DDR0_PS_MSK`, `RC32434_DDR0_DTYPE_BIT`, `RC32434_DDR0_DTYPE_MSK`, `RC32434_DDR0_RFC_BIT`, `RC32434_DDR0_RFC_MSK`, `RC32434_DDR0_RP_BIT`, `RC32434_DDR0_RP_MSK`, `RC32434_DDR0_AP_BIT`, `RC32434_DDR0_AP_MSK`, `RC32434_DDR0_RCD_BIT`, `RC32434_DDR0_RCD_MSK`, `RC32434_DDR0_CL_BIT`, and 50 more; 1 structs: `ddr_ram`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `ddr_ram` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/rb.h`. Major macro families are `RC32434_DDR0 (28)`, `RC32434_LLC (10)`, `RC32434_QSC (10)`, `RC32434_DCST (6)`, `RC32434_LLFC (4)`, `RC32434_DDRC (3)`, `RC32434_DLLED (3)`, `RC32434_DSCT (3)`. Typed contracts include `ddr_ram`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/ddr.h -->
