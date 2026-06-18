# sources/distributed-fs/openafs/src/util/test/dirpath_test.c

Purpose: Manual/smoke test for dirpath initialization, exported path macros, local path construction, and temp-directory lookup.

Important behavior: `main()` calls `initAFSDirPath()`, reports missing client/server path status flags, prints many `AFSDIR_*` macro results, tests `ConstructLocalPath()`, `ConstructLocalBinPath()`, `ConstructLocalLogPath()`, and prints `gettmpdir()`.

Control flow and state: The test allocates path buffers via construct functions, prints them, and frees them. It includes a Windows-only fully qualified drive path case. It does not assert expected values; it is observational.

Dependencies and integration: Includes `afs/afsutil.h`, roken, and stdio. Built by `util/test/Makefile.in` against `util.a` and `libopr.a`.

Risks and test signals: Because it prints rather than verifies, automated use needs output comparison or simple success checks. It exercises initialization side effects, canonical/local translation, and allocation ownership, making it useful after dirpath macro changes.
