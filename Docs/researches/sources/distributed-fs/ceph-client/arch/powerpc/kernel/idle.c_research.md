# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle.c

## Purpose
Implements the common PowerPC architecture idle entry wrapper, boot option disabling of platform power-save callbacks, and optional sysctl for Power4/970 nap mode.

## Important APIs, Types, And Functions
Exports `cpuidle_disable` and defines `arch_cpu_idle`, `powersave_off`, `power4_idle`, `powersave_nap`, and `register_powersave_nap_sysctl`. It uses platform callback `ppc_md.power_save`, runlatch helpers, HMT priority macros, and `prep_irq_for_idle`.

## Control Flow
`powersave=off` clears `ppc_md.power_save` and marks cpuidle disabled. `arch_cpu_idle` turns the runlatch off, calls the platform power-save routine when present, normalizes interrupt state by disabling local IRQs if the platform returned enabled, or otherwise drops hardware thread priority. It then restores medium priority and runlatch-on state. With `CONFIG_PPC_970_NAP`, `power4_idle` checks CPU support and `powersave_nap`, prepares IRQ state, flushes Altivec data streams if needed, and enters the assembly nap routine.

## State And Persistence
Persistent runtime state is `cpuidle_disable`, `powersave_nap`, and `ppc_md.power_save`. The sysctl under `kernel/powersave-nap` changes `powersave_nap` until reboot. No durable storage is used.

## Dependencies And Integration Points
Integrates with scheduler idle, PowerPC machdep callbacks, cpuidle policy, runlatch accounting, HMT thread priority, sysctl, timer/IRQ lazy masking, and assembly routines in `idle_book3s.S`. It relies on callers accepting either disabled or enabled interrupts after idle return.

## Risks And Edge Cases
The key risk is mismatched interrupt state around platform power-save code. `prep_irq_for_idle` must reject idle entry when a soft-masked interrupt is pending. Clearing `ppc_md.power_save` via boot option affects every CPU and disables deeper platform idle states. Power4 nap depends on CPU feature bits, user/sysctl enablement, and correct wakeup fixup.

## Test Signals
Signals include boot with and without `powersave=off`, idle loop residency, `/proc/sys/kernel/powersave-nap` behavior, interrupt wakeups from idle, runlatch accounting, scheduler idle tracing, and PowerMac/970 nap wakeup tests.
