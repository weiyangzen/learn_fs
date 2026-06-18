# sources/distributed-fs/ceph-client/kernel/time/Makefile

## Purpose
`kernel/time/Makefile` selects the compiled objects for the kernel time subsystem according to Kconfig symbols. It wires core timekeeping, timers, hrtimers, POSIX timers or stubs, tick/nohz infrastructure, namespaces, tests, and debug helpers into the build.

## Important APIs, types, and functions
- Always-built objects include `time.o`, `timer.o`, `hrtimer.o`, `sleep_timeout.o`, `timekeeping.o`, `ntp.o`, `clocksource.o`, `jiffies.o`, `timer_list.o`, `timeconv.o`, `timecounter.o`, and `alarmtimer.o`.
- POSIX timer selection builds `posix-timers.o`, `posix-cpu-timers.o`, `posix-clock.o`, and `itimer.o`, or `posix-stubs.o` when disabled.
- Conditional objects cover generic clockevents, tick broadcast, sched clock, oneshot/nohz, legacy tick, SMP timer migration, vsyscall gettimeofday, debugfs, udelay test, time namespaces, VDSO namespace support, clocksource watchdog test, and time KUnit tests.
- `CFLAGS_sched_clock.o += -DDISABLE_BRANCH_PROFILING` disables branch profiling for noinstr-unsafe sched clock code when branch profiling is enabled.

## Control flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` lines at build time. POSIX timers and broadcast support use `ifeq` blocks to select groups of objects. There is no runtime control flow in this file.

## State and persistence behavior
The file affects build artifacts only. It creates no runtime state, but the selected objects implement persistent kernel timekeeping behavior.

## Dependencies and integration points
It is directly driven by `kernel/time/Kconfig` and global architecture symbols. It integrates time subsystem sources with Kbuild and ensures stubs replace POSIX timer implementations when needed.

## Risks
Incorrect object selection can produce unresolved symbols, duplicate implementations, or missing runtime features. The branch profiling flag is important because scheduler clock noinstr paths cannot safely call profiling instrumentation.

## Test signals
Build all relevant config combinations: POSIX timers on/off, generic clockevents/broadcast on/off, SMP nohz, legacy tick, debugfs, time namespaces, VDSO namespace, watchdog test, and `TIME_KUNIT_TEST`. Link failures or missing syscall behavior are primary indicators.
