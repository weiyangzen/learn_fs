# sources/compression/zlib/contrib/blast/Makefile

Purpose: minimal standalone make build and test for the blast library.

Important targets: `libblast.so`, `blast-test`, `test`, `clean`, and default `all: test`.

Control flow: compiles `blast.c` into a shared library, builds `blast-test` against it, runs `blast-test < test.pk | cmp - test.txt` with `LD_LIBRARY_PATH=./`, and removes generated files on clean.

State and persistence: writes `libblast.so`, `blast-test.o`, and `blast-test`.

Dependencies and integration: uses system `cc`, `cmp`, shell redirection, and test fixtures `test.pk`/`test.txt`.

Risks: Unix/Linux oriented; no portability flags, install rules, or static build. Runtime loader setup is hard-coded to `LD_LIBRARY_PATH`.

Test signals: exact decompressed output comparison against `test.txt`.
