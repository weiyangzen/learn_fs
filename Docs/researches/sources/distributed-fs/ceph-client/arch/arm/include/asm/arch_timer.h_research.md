<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_timer.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_timer.h

## Purpose
ARM32 architectural timer accessors for the clocksource/clockevent driver.

## Important APIs/types/functions
- `arch_timer_arch_init()`
- CP15 timer accessors: `arch_timer_reg_write_cp15()`, `arch_timer_reg_read_cp15()`, `arch_timer_get_cntfrq()`, `__arch_counter_get_cntpct()`, `__arch_counter_get_cntvct()`, stable variants, `arch_timer_get_cntkctl()`, and `arch_timer_set_cntkctl()`.
- Event stream feature helpers: `arch_timer_set_evtstrm_feature()` and `arch_timer_have_evtstrm_feature()`.
- Erratum macros: `has_erratum_handler()` false and `erratum_handler()`.

## Control flow
Inline switch statements emit the correct CP15 read/write instruction for physical or virtual timer control and compare-value registers. Counter reads issue `isb()` before `mrrc`. Control writes issue `isb()` after writes.

## State and persistence behavior
State is architectural timer hardware state: control registers, compare values, frequency, kernel control, and advertised HWCAP event stream bit. No file-local storage exists.

## Dependencies and integration points
Depends on `clocksource/arm_arch_timer.h`, CP15 timer registers, barriers, HWCAP, and the generic ARM arch timer driver.

## Risks and edge cases
Unsupported access/register combinations use `BUILD_BUG()`. ARM32 declares no timer erratum handlers here, so affected hardware must be handled elsewhere or not supported. Counter reads require barriers for ordering.

## Test signals
Boot with `CONFIG_ARM_ARCH_TIMER`, verify clocksource registration, timer interrupts, virtual/physical timer modes, event stream HWCAP, and suspend/resume timer continuity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_timer.h -->
