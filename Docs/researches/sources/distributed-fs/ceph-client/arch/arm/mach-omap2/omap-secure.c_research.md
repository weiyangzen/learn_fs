<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.c

## Purpose
`omap-secure.c` implements secure monitor/ROM/OP-TEE call plumbing for OMAP low-power, cache-controller, SMP, RX-51 PPA, secure RAM save, and secure PM notifier paths.

## Important APIs, Types, and Functions
Public APIs include `omap_secure_dispatcher()`, `omap_smccc_smc()`, `omap_smc1()`, `omap_secure_ram_reserve_memblock()`, `omap3_save_secure_ram()`, `rx51_secure_update_aux_cr()`, `rx51_secure_rng_call()`, and `omap_secure_init()`. Important state is `omap_secure_memblock_base` and `optee_available`.

## Control Flow
`omap_secure_init()` detects an available `/firmware/optee` node. `omap_smc1()` dispatches either ARM SMCCC SiP SMC calls through OP-TEE-compatible calling convention or legacy OMAP ROM `_omap_smc1`. `omap_secure_dispatcher()` builds a per-CPU physical parameter buffer, flushes caches, and calls `omap_smc2()`. RX-51 dispatcher disables IRQ/FIQ, flushes caches, and calls `omap_smc3()`. A secure PM initcall registers a CPU cluster PM exit notifier on non-GP OMAP44xx to refresh ROM return address after OSWR/MPU off.

## State and Persistence Behavior
Reserved secure RAM storage is allocated from memblock. Static parameter buffers are temporary per-call state. Secure-world firmware owns persistent effects such as saved secure RAM, AUX control register updates, cache-controller secure registers, and ROM return addresses.

## Dependencies and Integration Points
It depends on ARM SMCCC, memblock, cache maintenance, OF firmware nodes, CPU PM notifiers, `omap-smc.S`, `omap-secure.h`, and SoC/device-type detection. It integrates with wakeupgen secure context save, SMP ACTLR/ACR programming, L2C310 secure writes, RX-51 RNG/ACR calls, and OMAP3 secure RAM save.

## Risks
Physical parameter buffers must be cache-clean before SMC. Calling the wrong ABI when OP-TEE is present or absent can fail silently or trap. IRQ/FIQ masking in RX-51 paths is sensitive. Secure calls are device-type and firmware-version dependent; failures can break low-power resume or security hardening.

## Test Signals
Boot GP and HS/EMU devices with and without OP-TEE nodes. Verify secure SMC return warnings, L2 secure register writes, OMAP4 GIC save on HS devices, RX-51 RNG/ACR paths where applicable, and suspend/resume after cluster PM exit. Confirm memblock reservation succeeds early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-secure.c -->
