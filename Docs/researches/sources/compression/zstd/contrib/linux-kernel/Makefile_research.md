# sources/compression/zstd/contrib/linux-kernel/Makefile

Purpose: generate, import, and test a Linux-kernel-shaped zstd source tree from upstream zstd.

Important behavior: `libzstd` deletes/recreates `linux/`, invokes `freestanding.py` with kernel-specific dependency rewrites, external xxhash mapping, SPDX insertion, disabled intrinsics/ASM/multithreading/legacy support, Linux/compiler macro choices, sanitizer disables, heap compression mode, and visibility/fallthrough replacements. It removes AMD64 assembly, moves public headers to `linux/include/linux`, copies the kernel wrapper header/modules/source lists, and installs `linux.mk` as the generated lib Makefile. `import` copies generated headers/lib into `$(LINUX)`. `import-upstream` copies raw upstream sources with selected removals. `test` regenerates and runs `make -C test run-test` with strict warnings.

State, dependencies, and integration: generated state is `contrib/linux-kernel/linux`. It depends on `freestanding.py`, kernel shim files, upstream lib layout, and test fixtures.

Risks and test signals: macro hardwiring is fragile when upstream internals change. The `test` target is the key signal, also exercised by `dev-short-tests` linux-kernel job.
