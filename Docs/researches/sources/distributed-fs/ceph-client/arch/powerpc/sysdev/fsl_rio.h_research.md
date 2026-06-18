<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.h

Purpose: shared Freescale RapidIO constants, register structures, private state structures, globals, and RMU helper declarations.

Important APIs/types/functions: macros for register windows and ATMU offsets, doorbell ROWAR flags, maximum message/port counts, structures `rio_atmu_regs`, `rio_inb_atmu_regs`, `rio_dbell_ring`, `rio_port_write_msg`, `fsl_rio_dbell`, `fsl_rio_pw`, `rio_priv`, extern globals `rio_regs_win`, `rmu_regs_win`, `rio_law_start`, `dbell`, `pw`, and declarations for RMU/doorbell/message/port-write functions.

Control flow: no executable logic. The structures define how `fsl_rio.c` and RMU support files share controller state and hardware register mappings.

State and persistence: the declared structures persist per controller or RMU unit: mport arrays, device pointers, MMIO register pointers, DMA rings/messages, IRQ numbers, work and FIFO state, maintenance windows, and message manager handles.

Dependencies and integration points: depends on Linux RapidIO core, kfifo, DMA address types, and companion RMU implementation files (`fsl_rmu.c` and related helpers). Used directly by `fsl_rio.c`.

Risks: register structure fields are raw 32-bit hardware registers and must remain offset-compatible. Global externs constrain the driver toward singleton hardware.

Test signals: successful build/link with RMU helpers, correct doorbell/port-write/message-unit operation, and valid register programming through `fsl_rio.c` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rio.h -->
