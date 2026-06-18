# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/Makefile

## Purpose
Selects the object files for the s390 diagnose support subdirectory.

## Important APIs, Types, And Functions
No C API is defined. The single Kbuild assignment links `diag_misc.o`, `diag324.o`, `diag.o`, and `diag310.o` into the parent `diag/` object list.

## Control Flow
At build time, Kbuild compiles the listed objects in order. This pulls in the `/dev/diag` misc device, DIAG 324 power-information ioctls, generic diagnose wrappers/statistics, and DIAG 310 memory-topology ioctls.

## State And Persistence
No runtime state is owned by the Makefile. Runtime state is in the selected C objects.

## Dependencies And Integration Points
Integrates the subdirectory with `arch/s390/kernel/Makefile`, which includes `obj-y += diag/`.

## Risks And Edge Cases
Removing an object breaks exported diagnose helpers or ioctl dispatch. Order changes are low risk but can affect link diagnostics and initcall placement visibility.

## Test Signals
Signals include s390 build/link success, `/dev/diag` registration, and feature-specific DIAG 310/324 tests.
