# sources/distributed-fs/ceph-client/drivers/cpuidle/Makefile

Purpose: maps CPU idle Kconfig symbols to framework, governor, DT helper, and platform driver objects.

Important build flow: core objects `cpuidle.o`, `driver.o`, `governor.o`, `sysfs.o`, and `governors/` always build within the directory. Optional objects include `coupled.o`, `dt_idle_states.o`, `dt_idle_genpd.o`, `poll_state.o`, and `cpuidle-haltpoll.o`. ARM, MIPS, POWERPC, and RISC-V driver objects are selected from their platform symbols, including the files in this group such as `cpuidle-arm.o`, `cpuidle-psci.o`, `cpuidle-powernv.o`, and `cpuidle-pseries.o`.

State and persistence behavior: no runtime state; it determines link-time availability. It also disables branch profiling for this directory when trace branch profiling is configured because idle code can include noinstr-sensitive paths.

Dependencies and integration points: depends on Kconfig symbols generated from top-level and arch-specific menus. Platform init code relies on the selected objects to register drivers at initcall time.

Risks and test signals: risks include missing object selection causing silent platform idle fallback to arch default idle, branch profiling incompatibility if flags are not applied, and stale platform symbols after Kconfig moves. Test signals are clean links for representative ARM/MIPS/POWERPC/RISC-V configs and expected cpuidle driver registration on boot.
