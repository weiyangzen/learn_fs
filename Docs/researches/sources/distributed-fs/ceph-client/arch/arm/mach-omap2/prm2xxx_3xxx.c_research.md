# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx_3xxx.c

## Purpose
Implements PRM functionality shared by OMAP2 and OMAP3: submodule hardreset operations, common powerdomain memory/logic operations, powerdomain transition polling, and clockdomain wake dependency manipulation.

## APIs, Flow, And State
Exports `omap2_prm_is_hardreset_asserted()`, `omap2_prm_assert_hardreset()`, and `omap2_prm_deassert_hardreset()`. Deassert flow checks for already-deasserted reset, clears status by writing one, clears the reset control bit, then uses `omap_test_timeout()` against `RM_RSTST`. Powerdomain functions set/read memory on/retention/status masks and logic retention through PRM RMW helpers. `omap2_pwrdm_wait_transition()` polls `OMAP_INTRANSITION_MASK`. Clockdomain dependency helpers set, clear, read, and bulk-clear `PM_WKDEP` bits while updating dependency usecounts.

## Dependencies And Integration
Depends on `powerdomain`, `clockdomain`, `prm2xxx_3xxx.h`, and OMAP24xx register bits. It is reused by OMAP2 and OMAP3 PRM low-level data tables and powerdomain operation tables.

## Risks And Test Signals
Hardreset deassert sequencing is timing-sensitive and can return `-EEXIST` or `-EBUSY`; callers must handle these outcomes. Clockdomain bulk clear assumes caller holds the powerdomain lock. Test signals are hwmod reset/deassert operations, powerdomain transition latency, wake dependency changes, and no timeout logs under suspend/resume.
