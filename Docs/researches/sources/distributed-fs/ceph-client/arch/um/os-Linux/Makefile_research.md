# sources/distributed-fs/ceph-client/arch/um/os-Linux/Makefile

## Purpose
Builds the host-Linux userspace support layer for UML.

## Important APIs, Types, and Functions
Lists core objects: ELF aux scanning, exec/path helpers, file/process/memory/IRQ/signal/time/TTY/UMID utilities, SKAS support, and optional SMP support. Disables KCOV instrumentation, adjusts frame-size warnings, and sets `USER_OBJS` for files compiled with user C flags.

## Control Flow, State, and Persistence
No runtime control flow. Build state controls which objects are compiled as user-side objects and how instrumentation is suppressed.

## Dependencies and Integration Points
Includes `arch/um/scripts/Makefile.rules`, pulls `skas/`, and conditionally builds `smp.o` for `CONFIG_SMP`. This layer is called by kernel-side UML code through `os.h` and related headers.

## Risks and Test Signals
Risks are accidentally instrumenting user-side code, omitting an object from `USER_OBJS`, or frame-size regressions in signal/main. Test allnoconfig/defconfig/SMP builds and clang/gcc warning behavior.
