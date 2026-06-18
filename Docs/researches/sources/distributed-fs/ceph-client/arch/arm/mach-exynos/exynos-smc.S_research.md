# sources/distributed-fs/ceph-client/arch/arm/mach-exynos/exynos-smc.S

Purpose: provides the ARM assembly wrapper for Samsung Exynos secure monitor calls.

Important APIs/types/functions: exports `exynos_smc`, which executes the SMC instruction with arguments in ARM calling-convention registers and returns to the caller.

Control flow: C callers pass command and arguments; the wrapper issues the monitor call and returns after secure firmware completes.

State and persistence: no software state; secure firmware may mutate hardware state according to command.

Dependencies and integration: paired with Exynos SMC command definitions in `smc.h` and used by Exynos firmware, power, cache, and SMP code.

Risks: SMC ABI is firmware-specific and failures may not be expressible as normal Linux errors. Calling it without secure firmware support can trap or hang.

Test signals: Exynos boot under secure firmware, CPU power/suspend operations using SMC, and build coverage for ARM assembly exports.
