# sources/distributed-fs/ceph-client/tools/include/nolibc/crt.h

## Purpose
Implements the architecture-independent C runtime startup handoff for nolibc programs.

## APIs, Types, and Functions
Declares weak globals `environ` and `_auxv`, init/fini array symbols, optional `program_invocation_name` and `program_invocation_short_name`, helper `__nolibc_program_invocation_short_name()`, and `_start_c(long *sp)`.

## Control Flow, State, and Persistence
`_start_c()` decodes the initial process stack into `argc`, `argv`, `envp`, and auxiliary vector, initializes stack canary state, sets program invocation names, runs preinit and init arrays, calls `main(argc, argv, envp)`, then runs fini arrays and exits with the returned status. Persistent process state is limited to the weak globals and program-name pointers.

## Dependencies and Integration
Depends on architecture `_start` stubs passing the initial stack pointer, `stackprotector.h`, `stdlib`/`string` helpers, ELF process stack layout, and linker-provided init/fini array boundaries. It is the bridge between raw kernel process entry and normal C `main()`.

## Risks and Test Signals
Risks include incorrect initial-stack parsing, constructor/destructor ordering bugs, missing stack-canary initialization before protected code, and weak symbol conflicts with embedding programs. Test signals are tiny nolibc executable startup tests, argv/envp/auxv validation, constructor/destructor ordering tests, stack-protector builds, and programs with and without `NOLIBC_NO_RUNTIME`.
