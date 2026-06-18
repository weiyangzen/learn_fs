# sources/distributed-fs/ceph-client/arch/powerpc/boot/4xx.c

## Purpose
PowerPC 4xx/44x boot-wrapper support for memory-size discovery, clock fixups, EBC ranges, Ethernet quiesce, and reset handling before the decompressed kernel starts.

## Important APIs, Types, And Control Flow
Memory helpers include `ibm4xx_sdram_fixup_memsize()`, `ibm440spe_fixup_memsize()`, and `ibm4xx_denali_fixup_memsize()`, which read SDRAM/MQ/Denali DCRs, account for selected chip errata, and call `dt_fixup_memory()`. Clock helpers (`ibm440gp_fixup_clocks()`, `ibm440ep_fixup_clocks()`, `ibm440gx_fixup_clocks()`, `ibm440spe_fixup_clocks()`) derive CPU/PLB/OPB/EBC/UART/timebase frequencies from CPC/CPR/SDR registers and write device-tree clock properties. `ibm4xx_fixup_ebc_ranges()` builds an EBC `ranges` property from active chip-select registers. `ibm4xx_quiesce_eth()` resets EMAC/MAL, and `ibm44x_dbcr_reset()` requests a system reset through DBCR0.

## State, Dependencies, Risks, And Tests
The file mutates the live flattened device tree and writes hardware DCR/Special Purpose Registers. Dependencies include `dcr.h`, `reg.h`, device-tree ops, and board wrappers that pass clock constants and node paths. Risks include wrong hard-coded sysclk/timer inputs, Denali chip-select workarounds for Sequoia/Rainier, overflow in memory-size arithmetic, incorrect EBC range packing, and hangs waiting for MAL reset. Test with 4xx board wrapper builds/boots, FDT property inspection, clock frequency validation against firmware, and memory sizing on SDRAM, MQ, and Denali controllers.
