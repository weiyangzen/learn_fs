<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h` provides machine-specific constants and declarations for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `__ASM_MACH_LOONGSON64_BUILTIN_DTBS_H_`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 6 extern variables: `__dtb_loongson64_2core_2k1000_begin`, `__dtb_loongson64c_4core_ls7a_begin`, `__dtb_loongson64c_4core_rs780e_begin`, `__dtb_loongson64c_8core_rs780e_begin`, `__dtb_loongson64g_4core_ls7a_begin`, `__dtb_loongson64v_4core_virtio_begin`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/builtin_dtbs.h -->
