<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/Makefile

## Purpose
Builds SGI/HPE UV platform BIOS, IRQ, RTC, and NMI support.

## Important APIs, Types, And Functions
`bios_uv.o`, `uv_irq.o`, `uv_time.o`, and `uv_nmi.o` are selected by `CONFIG_X86_UV`.

## Control Flow
Kbuild links all core UV platform support as a unit.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
These objects integrate with EFI runtime, x86 IRQ domains, clocksource/events, APIC, NMI, kdump, kgdb/kdb, and UV hub MMR infrastructure.

## Risks And Edge Cases
The objects are tightly platform-specific; building them without the right Kconfig guards would add unavailable hardware paths.

## Test Signals
UV config builds and boots on hubbed and hubless UV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/Makefile -->
