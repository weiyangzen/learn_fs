<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h` customizes I/O port byte-lane/address swizzling for `mach-ip32`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 5 macros including `__ASM_MACH_IP32_MANGLE_PORT_H`, `__swizzle_addr_b`, `__swizzle_addr_w`, `__swizzle_addr_l`, `__swizzle_addr_q`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (5)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is generic MIPS port I/O helpers, PCI/ISA-style drivers, bus endian translation, and platform-specific bridge windows.

## Risks
bad swizzle rules silently corrupt byte/word I/O against legacy devices.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-ip32/mangle-port.h -->
