# sources/distributed-fs/ceph-client/tools/spi/Makefile

Purpose: builds, cleans, and installs the SPI userspace test utilities `spidev_test` and `spidev_fdx`.

Important APIs, types, and functions: variables include `bindir`, `srctree`, `CFLAGS`, `ALL_TARGETS`, `ALL_PROGRAMS`, `SPIDEV_TEST_IN`, and `SPIDEV_FDX_IN`. Targets are `all`, `prepare`, object aggregation targets, final program link targets, `clean`, `install`, and `FORCE`.

Control flow: if `srctree` is unset, it is inferred two directories above `CURDIR`. Built-in make rules are disabled with `MAKEFLAGS += -r`. `prepare` creates `$(OUTPUT)include/linux/spi` and symlinks UAPI SPI headers from the kernel tree so the utilities can build outside the source tree. Per-program intermediate objects are produced through `tools/build/Makefile.include`; final binaries are linked with `$(CC)`. `install` copies built programs into `$(DESTDIR)$(bindir)`.

State and persistence: generated binaries and object/dependency/cmd files live under `$(OUTPUT)` when set, otherwise the source directory. Header symlinks are generated under `$(OUTPUT)include/`. `clean` removes binaries, generated include directory, and object/dependency artifacts.

Dependencies and integration points: depends on kernel tools build infrastructure, UAPI SPI headers, GNU make, compiler/linker variables, and `../scripts/Makefile.include`.

Risks: symlink target `$@` is the directory path, so the commands rely on `ln -sf <file> <dir>` semantics. In-source builds can delete matching object files under the current directory. Header symlinks can become stale if the source tree moves.

Test signals: `make -C tools/spi` should produce `spidev_test` and `spidev_fdx`; `make install DESTDIR=...` should install both. `make clean` should remove generated include links and build outputs.
