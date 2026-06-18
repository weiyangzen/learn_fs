# sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/Makefile

Purpose: this kselftest Makefile registers and builds the IA-64 `aliasing-test` program.

Important APIs and variables: `TEST_PROGS := aliasing-test` declares the executable as a runnable selftest program. `all: $(TEST_PROGS)` makes the default target build it. `include ../lib.mk` imports kselftest build/install/run rules. `clean` removes the generated executable.

Control flow: GNU make resolves `all`, lets the default implicit C compilation build `aliasing-test` from `aliasing-test.c`, and relies on `../lib.mk` for kselftest packaging and execution integration.

State and persistence: creates the `aliasing-test` binary in the source/build directory and deletes it on `make clean`.

Dependencies and integration points: integrates with the kselftest make framework and the adjacent C source. It is architecture-scoped by directory rather than by conditional logic in this Makefile.

Risks: no explicit compiler flags are set here; behavior depends on inherited `lib.mk` and environment. Removing only `$(TEST_PROGS)` is simple but broad through `rm -fr`.

Test signals: successful build produces the executable; kselftest execution signals come from the C program.
