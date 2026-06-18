# sources/distributed-fs/ceph-client/arch/um/kernel/skas/Makefile

## Purpose
Builds the UML SKAS kernel-side objects and the embedded stub executable used for user address-space helper processes.

## Important APIs, Types, and Functions
Defines `obj-y` for `stub.o`, `mmu.o`, `process.o`, `syscall.o`, `uaccess.o`, and `stub_exe_embed.o`. Builds `stub_exe.dbg` with a custom `STUB_EXE` link command, strips it into `stub_exe`, then embeds it through `stub_exe_embed.S`.

## Control Flow, State, and Persistence
The build flow compiles `stub_exe.o`, links a static no-stdlib executable with `STUB_EXE_LDFLAGS = -Wl,-n -static`, strips it, and treats the result as an object dependency for embedding. No runtime state is present.

## Dependencies and Integration Points
Includes `arch/um/scripts/Makefile.rules`, disables profiling/hardening for stub objects, disables KCOV, and filters profiling/gcov flags from the stub executable. It feeds `os-Linux/skas/process.c`, which writes the embedded executable into a memfd or temp file at boot.

## Risks and Test Signals
Risks are accidental instrumentation, hardening flags requiring unavailable registers, or stub binary rebuild dependency breakage. Test by clean-building UML with gcc/clang, profiling/gcov/KCOV configs, and verifying `stub_exe_start`/`stub_exe_end` produce a runnable stub.
