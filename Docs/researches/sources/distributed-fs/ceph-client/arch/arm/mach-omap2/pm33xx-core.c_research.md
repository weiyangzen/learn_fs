# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm33xx-core.c

## Purpose
`pm33xx-core.c` provides AM33xx/AM43xx architecture PM callbacks, cpuidle glue, and platform data for the `pm33xx` driver. It coordinates powerdomains, clockdomains, SCU mode, secure monitor calls, context save/restore, SRAM address lookup, and initial suspend blocking until firmware support is ready.

## Important APIs, Types, and Functions
Important functions include `amx3_common_pm_init()`, `am33xx_suspend_init()`, `am43xx_suspend_init()`, `am33xx_suspend()`, `am43xx_suspend()`, `am33xx_cpu_suspend()`, `am43xx_cpu_suspend()`, `amx3_idle_init()`, and `amx3_idle_enter()`. Key data types are `struct am33xx_pm_platform_data` and `struct amx3_idle_state`.

## Control Flow
Common PM init registers a `pm33xx` platform device carrying SoC-specific ops and installs blocked suspend ops. The driver later calls init ops with an SRAM idle function. Suspend powers down GFX, enters CPU suspend, performs AM33xx GFX clockdomain wake/sleep workaround, or for AM43xx switches SCU modes and calls secure monitor suspend/resume on HS devices. Cpuidle parses `cpu-idle-states` phandles and maps `ti,idle-wkup-m3` to WFI flags.

## State and Persistence Behavior
Static state tracks powerdomain and clockdomain pointers, SCU mapping, `idle_fn`, and allocated `idle_states`. Hardware state includes GFX/CEFUSE domain targets, SCU power mode, INTC context, and AM43xx secure-side suspend state.

## Dependencies and Integration Points
It depends on cpuidle, platform suspend, wkup_m3 IPC, RTC, OMAP secure calls/SMCCC, clockdomain/powerdomain frameworks, SRAM support, AM33xx/AM43xx PRCM, and `pm33xx` platform data consumers.

## Risks
Suspend requires firmware and wkup_m3 IPC; premature suspend is blocked. Wrong SCU or secure-call handling can hang AM43xx resume. AM33xx GFX_L4LS workaround is required to avoid clockdomain transition stalls.

## Test Signals
Boot AM335x/AM437x, confirm `pm33xx` platform device registration and blocked suspend warning before firmware. With firmware, test standby/deepsleep, RTC wake, wkup_m3 idle states, GFX domain transition logs, INTC context restore, and HS/OP-TEE secure suspend/resume.
