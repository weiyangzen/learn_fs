# sources/distributed-fs/ceph-client/drivers/memory/ti-emif-pm.c

Purpose: This driver loads TI AM33xx/AM43xx EMIF low-power routines into on-chip SRAM, prepares data/function tables used by suspend/resume code, configures an EMIF self-refresh erratum workaround, and exports helpers for other PM code to discover SRAM function addresses and current memory type.

Important APIs/types/functions: `struct ti_emif_data` owns SRAM code/data physical and virtual addresses, gen_pool handles, `struct ti_emif_pm_data`, and `struct ti_emif_pm_functions`. `ti_emif_alloc_sram()` allocates code/data SRAM and computes virtual suspend and physical resume addresses. `ti_emif_push_sram()` copies assembly code and PM data into SRAM with `sram_exec_copy()`. Exported functions are `ti_emif_copy_pm_function_table()` and `ti_emif_get_mem_type()`. Probe/remove and PM callbacks manage lifecycle.

Control flow: Probe maps EMIF registers, records physical base, writes the 8192-cycle self-refresh delay, allocates SRAM, copies code/data, and publishes the singleton `emif_instance`. Resume checks whether SRAM still contains the code and recopies if context was lost. Remove clears the singleton and frees pools.

State and persistence: `emif_instance` is global singleton state, so only one active EMIF instance is supported. SRAM contains executable PM code and data across low-power transitions unless SRAM context is lost. Hardware EMIF registers hold erratum delay settings.

Dependencies and integration: Depends on `linux/sram.h`, genalloc pools, `linux/ti-emif-sram.h`, platform resources, OF match data, and `emif.h`. It integrates with the ARM assembly in `ti-emif-sram-pm.S` and external PM code that copies the function table.

Risks and test signals: Risks include missing SRAM pools, wrong virtual/physical address choice for suspend versus resume, singleton misuse, and SRAM contents becoming stale after resume. Test signals include successful SRAM allocation/copy, exported function-table copy, correct DDR type from `ti_emif_get_mem_type()`, suspend/resume on AM335x/AM437x, and no EMIF self-refresh erratum symptoms.
