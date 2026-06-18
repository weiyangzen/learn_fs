<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/Makefile

## Purpose
Builds Intel Quark Isolated Memory Region support and optional debug selftests.

## Important APIs, Types, And Functions
`imr.o` is selected by `CONFIG_INTEL_IMR`; `imr_selftest.o` is selected by `CONFIG_DEBUG_IMR_SELFTEST`.

## Control Flow
Kbuild includes the IMR driver and, optionally, the selftest initcall.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
Depends on the Intel Quark platform and IOSF MBI driver that the IMR implementation uses.

## Risks And Edge Cases
Enabling selftests on production hardware can temporarily create and remove IMRs, so the debug symbol should stay opt-in.

## Test Signals
Builds with and without `CONFIG_DEBUG_IMR_SELFTEST` should link cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/Makefile -->
