# sources/distributed-fs/ceph-client/tools/dma/Makefile

Purpose: Builds and installs `dma_map_benchmark`, a userspace frontend for the kernel DMA map benchmark debugfs interface.

Important APIs, types, and functions: Defines `srctree`, `CFLAGS`, `ALL_TARGETS`, `prepare` symlink for `linux/map_benchmark.h`, direct compile rule for `dma_map_benchmark`, `clean`, and `install`.

Control flow: `all` builds the program. `prepare` creates `$(OUTPUT)include/linux/map_benchmark.h` symlink from UAPI. The target compiles `dma_map_benchmark.c` directly. Install copies built programs to `bindir`.

State and persistence: Creates binary, output include symlink, and build artifacts; install writes destination binary.

Dependencies and integration points: Uses tools build include, UAPI `linux/map_benchmark.h`, and supports both tools and selftests build contexts.

Risks: Compile rule targets `dma_map_benchmark` in the current directory rather than `$(OUTPUT)dma_map_benchmark`, while `ALL_PROGRAMS` uses `$(OUTPUT)%`; this is existing behavior to watch in out-of-tree builds. Clean removes output include and generated files.

Test signals: In-tree make, `OUTPUT=` builds, selftests environment with `srctree=.`, install, and clean.
