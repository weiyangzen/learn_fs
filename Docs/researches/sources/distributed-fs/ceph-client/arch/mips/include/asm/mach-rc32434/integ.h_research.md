<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 14 macros including `__RC32434_INTEG_H__`, `INTEG0_BASE_ADDR`, `RC32434_ERR_WTO`, `RC32434_ERR_WNE`, `RC32434_ERR_UCW`, `RC32434_ERR_UCR`, `RC32434_ERR_UPW`, `RC32434_ERR_UPR`, `RC32434_ERR_UDW`, `RC32434_ERR_UDR`, `RC32434_ERR_SAE`, `RC32434_ERR_WRE`, `RC32434_WTC_EN`, `RC32434_WTC_TO`; 1 structs: `integ`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `integ` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `asm/mach-rc32434/rb.h`. Major macro families are `RC32434_ERR (10)`, `RC32434_WTC (2)`, `INTEG0_BASE (1)`, `_ (1)`. Typed contracts include `integ`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/integ.h -->
