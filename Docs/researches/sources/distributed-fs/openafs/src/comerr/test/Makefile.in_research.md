# sources/distributed-fs/openafs/src/comerr/test/Makefile.in

Purpose: Autoconf Makefile template for the comerr self-test program.

Important APIs/types/functions: defines `srcdir`, includes `Makefile.config`, sets library search paths in `LDIRS`, builds `test` from `test.o`, `test1.o`, and `test2.o`, and relies on suffix rules from the surrounding build to generate `test1.c/.h` and `test2.c/.h` from `.et` files via `compile_et`.

Control flow: the default `all` target builds `test`; object dependencies force generated headers/sources to exist; `clean` removes generated `.et` outputs, objects, local tools, and test binaries. `install` and `dest` are intentionally no-op for this test directory.

State and persistence: writes only build artifacts in the object directory, notably generated error-table C/header files and the `test` executable. No installed state is produced.

Dependencies and integration: integrates the comerr test into the OpenAFS build rules through `AFS_LDRULE`, `${TOP_LIBDIR}`, `${DESTDIR}/lib/afs`, and `-lafscom_err`.

Risks and test signals: risks are stale generated files under parallel make, missing `compile_et` generation rules, and link-path mismatches. A successful `make test` build and execution of the resulting binary are the primary signals.
