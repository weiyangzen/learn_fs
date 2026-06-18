<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/Makefile

## Purpose

The memblock `Makefile` builds the user-space memblock simulator and test binary. It compiles a copy of the kernel `mm/memblock.c` together with tool-side stubs and memblock API tests under AddressSanitizer and UndefinedBehaviorSanitizer.

## Important APIs, Types, and Functions

Targets and variables define the build contract: `TARGETS = main`, `TEST_OFILES` includes allocation, helper, basic, NUMA, and exact-NID suites, `DEP_OFILES` includes `memblock.o`, `lib/slab.o`, `mmzone.o`, `slab.o`, and `cmdline.o`, and `EXTR_SRC = ../../../mm/memblock.c`. `BUILD=32` adds `-m32`; included `scripts/Makefile.include` processes user parameters such as `NUMA`, `MEMBLOCK_DEBUG`, and address-size options.

## Control Flow

The default `main` target links all object files. The `include` target creates local symlinks for kernel headers and x86 asm helpers, while `memblock.c` symlinks the real kernel implementation into the simulator directory. `clean` removes binaries, objects, and generated symlinks. `help` prints supported knobs.

## State and Persistence Behavior

Build state consists of object files, `main`, and symlinks under `linux/`, `asm/`, and `memblock.c`. Sanitizer instrumentation is part of every normal build. No test results are persisted by the Makefile itself.

## Dependencies and Integration Points

It depends on a kernel source tree layout, libasan, liburcu development packages, tool include directories, and shared scripts under `tools/scripts`. It integrates real kernel memblock code with user-space stubs in this directory and with test entrypoint `main.c`.

## Risks and Edge Cases

Symlink creation assumes relative paths remain valid. The simulator includes kernel C directly, so changes in kernel headers can require new stubs. Sanitizer flags may expose host compiler/runtime requirements. `BUILD=32` requires 32-bit toolchain and libraries.

## Test Signals

Successful `make` should produce `main`; running it should execute all memblock suites. `make clean` should remove generated symlinks and objects. Building with `NUMA=1`, `MEMBLOCK_DEBUG=1`, and `BUILD=32` exercises important alternate configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/Makefile -->
