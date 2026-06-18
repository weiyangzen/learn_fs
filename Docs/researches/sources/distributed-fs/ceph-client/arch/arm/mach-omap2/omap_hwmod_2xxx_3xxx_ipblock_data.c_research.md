# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_2xxx_3xxx_ipblock_data.c

Purpose: Supplies small shared class descriptors for IP blocks common to OMAP2 and OMAP3 data files. It avoids duplicating class/sysconfig definitions for UART, VENC, L3, L4, MPU, IVA, and HDQ/1-wire.

Important descriptors: `omap2_uart_class` uses `omap2_uart_sysc`, with OMAP2-style revision/sysconfig/sysstatus offsets, SIDLE, wakeup, softreset, autoidle, and SYSSTATUS reset-done support. `omap2_venc_hwmod_class` is a simple VENC class without sysconfig data. `l3_hwmod_class`, `l4_hwmod_class`, `mpu_hwmod_class`, and `iva_hwmod_class` are simple bus/initiator classes used by both 2xxx and 3xxx module data. `omap2_hdq1w_class` uses OMAP2 type1 sysconfig and a custom `omap_hdq1w_reset` hook.

Control flow: there is no executable function in this file. Other data files reference these exported class objects while constructing `struct omap_hwmod` records; the core then consumes the class sysconfig and reset hooks during `_init()`, `_setup_reset()`, `_enable_sysc()`, and `_idle_sysc()`.

State and persistence: the file contains static descriptor state only. At runtime, classes influence how the core reads/writes SYSCONFIG, waits for softreset completion, and applies custom reset behavior. UART descriptors using this class inherit smart-idle-capable sysconfig, wakeup enable handling, and softreset support.

Dependencies and integration: depends on `omap_hwmod_common_data.c` for `omap_hwmod_sysc_type1`, `hdq1w.h` for `omap_hdq1w_reset`, and OMAP DMA headers because UART class users may integrate with DMA-capable serial blocks. The exported classes are used by OMAP2420, OMAP2430, and OMAP3 data files.

Risks: because these classes are shared across generations, any sysconfig flag change affects many UART or HDQ instances. UART wakeup/autoidle behavior depends on matching real hardware offsets; a mismatch would show up as softreset or idle failures across multiple SoCs. Simple classes without sysconfig data intentionally skip register setup; adding sysconfig blindly to bus/initiator classes could cause missing-reg mapping failures.

Test signals: build/link should confirm all exported class symbols are available to the SoC data objects. Runtime signals are UART reset/idle/wakeup behavior on OMAP2 and OMAP3, HDQ custom reset success, and absence of hwmod warnings about missing sysconfig fields for shared UART/HDQ modules.
