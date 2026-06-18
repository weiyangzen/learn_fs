<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h` describes low-level controller registers and helper macros for `mach-loongson2ef/cs5536`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_CS5536_VSM_H`, `DECLARE_CS5536_MODULE`; 0 structs: none; 0 enums: none; 1 callable helpers/prototypes: `_read_reg`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `_read_reg`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/types.h`. Major macro families are `DECLARE_CS5536 (1)`, `_CS5536 (1)`. Typed contracts include no structs. Callable helpers or declarations include `_read_reg`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_vsm.h -->
