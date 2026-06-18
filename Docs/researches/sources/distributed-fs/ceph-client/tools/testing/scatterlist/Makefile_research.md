# sources/distributed-fs/ceph-client/tools/testing/scatterlist/Makefile

Purpose: builds a userspace scatterlist test harness with copied/generated kernel scatterlist sources and lightweight Linux header stubs.

Important APIs/types/functions: sets include paths, debug/O2/warnings, AddressSanitizer and UBSan flags; supports `BUILD=32`; builds `main` from `main.o scatterlist.o`; `include` target creates `linux/` and `asm/` stubs and copies `include/linux/scatterlist.h`; `scatterlist.c` target uses `sed` to remove `static`, `__always_inline`, and `inline` from kernel `lib/scatterlist.c`.

Control flow: `targets` depends on `include` and binary build; `clean` removes copied/generated headers, source, object files, binary, and `asm` directory.

State and persistence: creates generated files in the test directory during build.

Dependencies/integration: imports kernel scatterlist implementation into a userspace test binary and relies on local `linux/mm.h`/generated stubs.

Risks and test signals: source rewriting via `sed` is brittle if kernel code depends on inlining/static semantics. Sanitizer-enabled build and test execution are the main signals.
