<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/Makefile

## Purpose
Builds OLPC platform core, OpenFirmware/device-tree support, XO-1 power/RTC/SCI support, XO-1.5 SCI support, and low-level wakeup assembly.

## Important APIs, Types, And Functions
Objects include `olpc.o`, `olpc_ofw.o`, `olpc_dt.o`, `olpc-xo1-pm.o`, `xo1-wakeup.o`, `olpc-xo1-rtc.o`, `olpc-xo1-sci.o`, and `olpc-xo15-sci.o`, controlled by the corresponding OLPC Kconfig symbols.

## Control Flow
Kbuild includes platform-core objects for `CONFIG_OLPC` and then adds model-specific features by config.

## State And Persistence
No runtime state is in the Makefile; object selection determines which initcalls and platform drivers exist.

## Dependencies And Integration Points
Integrates OLPC code with x86 platform, PM, RTC, ACPI, input, EC, and OpenFirmware paths.

## Risks And Edge Cases
Model-specific object selection affects wake capability. For example XO-1 EC wakeups depend on XO-1 SCI support, and XO-1 suspend depends on wakeup assembly being linked.

## Test Signals
Config matrix builds for base OLPC, XO-1 PM/RTC/SCI, and XO-1.5 SCI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/Makefile -->
