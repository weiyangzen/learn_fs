# sources/distributed-fs/openafs/src/util/test/Makefile.in

Purpose: Builds utility test programs for dirpath and base conversion helpers.

Important targets: `all` / `tests` build `dirpath_test`, `b64`, and `fb64`. Each target links its object with `../util.a`, `libopr.a`, roken, and platform libraries. `clean` removes objects and generated test binaries.

Control flow and state: Makefile template includes configured `Makefile.config` and `Makefile.lwp`, then relies on standard OpenAFS build variables such as `AFS_LDRULE`, `TOP_LIBDIR`, `LIB_roken`, and `XLIBS`.

Dependencies and integration: Lives under `src/util/test` and validates parts of the utility library. It does not build `b32` in the listed `all` target even though `b32.c` exists.

Risks and test signals: The test set is narrow and largely command-line round-trip validation. Platform guards in individual test files may cause a built test to print "not required" and exit nonzero on unsupported platforms. Running `make tests` in this directory is the direct signal.
