<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.h

## Purpose
`omap-secure.h` defines secure monitor API indices, flags, return codes, secure RAM sizes, RX-51 PPA IDs, and prototypes for OMAP secure-call infrastructure.

## Important APIs, Types, and Functions
Important constants include `API_HAL_RET_VALUE_*`, `FLAG_START_CRITICAL`, `OMAP_SECURE_RAM_STORAGE`, `OMAP3_SAVE_SECURE_RAM_SZ`, OMAP4 HAL save indices, OMAP4/5 monitor indices, PPA service IDs, and RX-51 PPA IDs. It declares `omap_secure_dispatcher()`, `omap_smccc_smc()`, `omap_smc1()`, `omap_smc2()`, `omap_smc3()`, `omap_secure_ram_reserve_memblock()`, `save_secure_ram_context()`, `omap3_save_secure_ram()`, RX-51 helpers, `optee_available`, `omap_secure_init()`, and `set_cntfreq()`.

## Control Flow
The header has no runtime flow. It conditionally exposes C prototypes outside assembler and provides an inline no-op `set_cntfreq()` when realtime counter support is absent.

## State and Persistence Behavior
It declares `optee_available` but stores no state itself. Constants describe secure-world persistent operations and reserved RAM sizes used elsewhere.

## Dependencies and Integration Points
It depends on `linux/types.h` and, outside assembler, on kernel type definitions. It integrates `omap-secure.c`, `omap-smc.S`, SMP, wakeupgen, L2 cache, and low-power code.

## Risks
Incorrect service IDs or flags can call the wrong secure firmware function. The misspelled `API_HAL_RET_VALUE_SERVICE_UNKNWON` is ABI spelling in code and should not be casually renamed without updating users. Size constants affect reserved memory and secure RAM save compatibility.

## Test Signals
Compile C and assembly users. Runtime tests are secure dispatcher success, OP-TEE detection, L2 secure writes, GIC secure save, RX-51 secure calls, and absence of unresolved symbols for `set_cntfreq()` across configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.h -->
