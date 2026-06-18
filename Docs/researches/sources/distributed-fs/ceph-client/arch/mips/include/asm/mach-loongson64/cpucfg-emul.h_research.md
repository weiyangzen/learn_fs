<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h` provides machine-specific constants and declarations for `mach-loongson64`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_ASM_MACH_LOONGSON64_CPUCFG_EMUL_H_`, `LOONGSON_FPREV_MASK`; 0 structs: none; 0 enums: none; 3 callable helpers/prototypes: `loongson3_cpucfg_emulation_enabled`, `loongson3_cpucfg_read_synthesized`, `loongson3_cpucfg_synthesize_data`; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `loongson3_cpucfg_emulation_enabled`, `loongson3_cpucfg_read_synthesized`, `loongson3_cpucfg_synthesize_data`. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `asm/cpu-info.h`, `loongson_regs.h`. Major macro families are `LOONGSON_FPREV (1)`, `_ASM (1)`. Typed contracts include no structs. Callable helpers or declarations include `loongson3_cpucfg_emulation_enabled`, `loongson3_cpucfg_read_synthesized`, `loongson3_cpucfg_synthesize_data`. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson64/cpucfg-emul.h -->
