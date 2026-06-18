<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 101 macros including `__ASM_RC32434_ETH_H`, `ETH0_BASE_ADDR`, `ETH_INT_FC_EN`, `ETH_INT_FC_ITS`, `ETH_INT_FC_RIP`, `ETH_INT_FC_JAM`, `ETH_INT_FC_OVR`, `ETH_INT_FC_UND`, `ETH_INT_FC_IOC`, `ETH_FIFI_TT_TTH_BIT`, `ETH_FIFO_TT_TTH`, `ETH_ARC_PRO`, `ETH_ARC_AM`, `ETH_ARC_AFM`, `ETH_ARC_AB`, `ETH_SAL_BYTE_5`, `ETH_SAL_BYTE_4`, `ETH_SAL_BYTE_3`, `ETH_SAL_BYTE_2`, `ETH_SAH_BYTE1`, `ETH_SAH_BYTE0`, `ETH_GPF_PTV`, `ETH_PFS_PFD`, `ETH_CFSA0_CFSA4`, and 77 more; 1 structs: `eth_regs`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `eth_regs` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `ETH_TX (18)`, `ETH_RX (17)`, `ETH_MAC2 (13)`, `ETH_MII (10)`, `ETH_INT (7)`, `ETH_MAC1 (6)`, `ETH_ARC (4)`, `ETH_CFSA1 (4)`. Typed contracts include `eth_regs`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; the file contains 101 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/eth.h -->
