# sources/compression/zstd/contrib/seqBench/Makefile

Purpose: builds the experimental `seqBench` utility against the local zstd source tree and selected program/common helper objects. It is a focused contrib Makefile for sequence-generation/compression benchmarking rather than a general library build.

Important variables/targets: `PROGDIR`, `LIBDIR`, `LIBZSTD`, include `CPPFLAGS`, strict warning `DEBUGFLAGS`, `default`, `all`, `seqBench`, `$(LIBZSTD)`, object rules for `benchfn.o`, `timefn.o`, `datagen.o`, `util.o`, `xxhash.o`, and `clean`.

Control flow: `seqBench` depends on helper objects, `seqBench.c`, and `../../lib/libzstd.a`; the library target recursively invokes `make -C ../../lib libzstd.a` with propagated `CFLAGS`. Each helper object is compiled directly from the programs or common source directory into the contrib directory. `clean` removes local objects, asks the library directory to clean, and deletes the binary.

State and persistence: generated state consists of local `.o` files and the `seqBench` executable plus the library build artifacts under `../../lib`. No runtime state is tracked.

Dependencies/integration: integrates with `../../programs` helper sources and `../../lib`. It assumes GNU-ish make behavior, a C compiler, archive build support in `lib/Makefile`, and warning flags accepted by the selected compiler.

Risks: the recipe compiles `$^`, so dependency ordering matters and adding headers as prerequisites would accidentally pass them to the compiler/linker. `clean` delegates to the library clean target, which can remove artifacts outside this contrib tool. The target is not portable to non-make build systems and is tied to source-tree-relative layout.

Test signals: `make -C contrib/seqBench`, `./seqBench <sample>`, and `make clean` should build, validate sequence compression, and remove generated files without affecting unrelated workspace state beyond the library clean contract.
