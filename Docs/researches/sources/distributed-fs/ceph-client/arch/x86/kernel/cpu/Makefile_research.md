# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/Makefile

## Purpose
This Makefile selects and configures x86 CPU feature, topology, vendor, hypervisor, mitigation, and generated capability-name objects.

## Important APIs, Types, and Functions
The core object list includes cache info, topology, common CPU identification, RDRAND, matching, CPU bug handling, APERF/MPERF, CPUID dependencies, UMWAIT, and generated `capflags.o`/`powerflags.o`. Conditional objects add local APIC topology, procfs, Intel/AMD/Hygon and other vendor files, MCE, MTRR, microcode, resctrl, SGX, perf watchdog, hypervisor guests, debugfs, bus lock detection, and generated `capflags.c`.

## Control Flow
kbuild expands `obj-y` and `obj-$(CONFIG_*)` based on configuration. It also removes tracing from early secondary CPU boot-sensitive objects and disables KCOV/KMSAN/KCSAN instrumentation for code paths that can hang when instrumented. The `mkcapflags` rule regenerates `capflags.c` from `cpufeatures.h`, `vmxfeatures.h`, and `mkcapflags.sh`.

## State and Persistence
There is no runtime state. Persistent outputs are selected built objects and generated `capflags.c`.

## Dependencies and Integration Points
It integrates with architecture Kconfig, kbuild, tracing and sanitizer instrumentation policy, CPU vendor support files, hypervisor detection files, and generated feature string tables.

## Risks and Test Signals
Risks include missing object selection for a configured CPU vendor or hypervisor, unsafe instrumentation on early CPU boot code, and stale generated capability strings. Test signals include config matrix builds, generated `capflags.c` updates when feature headers change, and boot tests with tracing/sanitizers enabled.
