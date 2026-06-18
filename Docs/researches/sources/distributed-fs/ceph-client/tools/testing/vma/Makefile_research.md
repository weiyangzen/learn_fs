<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/vma/Makefile

## Purpose

The VMA `Makefile` builds the userspace VMA test binary that imports kernel VMA code and runs it against compatibility stubs.

## Important APIs, Types, and Functions

It includes `../shared/shared.mk`, sets `OFILES = $(SHARED_OFILES) main.o shared.o maple-shim.o`, builds target `vma`, and adds `-DNUM_VMA_FLAG_BITS=128 -DNUM_MM_FLAG_BITS=128`. The `main.o` dependency list includes local tests and kernel `mm/vma*.c` sources. `clean` removes targets, objects, generated shared files, and generated config headers.

## Control Flow and State

Make builds shared infrastructure first, then local and imported VMA objects, then links with sanitizer, pthread, and liburcu flags from `shared.mk`. Generated headers and transformed sources are build-state artifacts.

## Dependencies and Integration Points

It depends on shared userspace testing infrastructure, maple-tree shim, kernel mm sources, local VMA tests, and sanitizer-capable toolchains. It integrates kernel VMA logic with the standalone tools/testing/vma harness.

## Risks and Test Signals

Risks include stale object dependencies when kernel mm headers change, mismatched flag-bit counts, missing sanitizer runtimes, and kernel source drift requiring new stubs. A successful `make` and passing `./vma` run validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/vma/Makefile -->
