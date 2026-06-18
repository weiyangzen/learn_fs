# sources/compression/zstd/contrib/linux-kernel/test/Makefile

Purpose: user-space test harness Makefile for the generated Linux-kernel zstd source tree.

Important behavior: points `LINUX` to `../linux`, derives generated source/object lists from module/common/compress/decompress directories, adds include paths for generated linux headers, generated zstd lib, and local shim headers, defines `NDEBUG`, disables deprecated warnings, and sets `ZSTD_ASAN_DONT_POISON_WORKSPACE` because static workspace reuse conflicts with poisoning. It builds assembly objects, archives `liblinuxzstd.a`, links `test` against it, builds `static_test`, and `run-test` executes `macro-test.sh`, `test`, and `static_test`. `clean` removes generated objects and local test binaries/libs.

State, dependencies, and integration: state is generated object files, archive, and test executables. It integrates generated kernel sources with local fake Linux headers.

Risks and test signals: wildcard object selection may hide missing-source intent changes. `run-test` is the main validation gate for generated kernel import.
