<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/pe-file.c

## Purpose

This tiny C source is the origin for the PE fixture consumed by `pe-file-parsing.c`. It exists to produce `pe-file.exe` and `pe-file.exe.debug` with a deterministic build-id and debuglink setup.

## Research

The file exports only `main`, returning zero. The comments document the exact MinGW and objcopy commands used to create the checked-in PE binary, split debug file, compressed debug sections, stripped executable, and GNU debuglink. There is no runtime state or persistence in the program itself; the persistent artifact is the generated PE/debug fixture stored beside perf tests. Dependencies are external to compilation: `x86_64-w64-mingw32-gcc` and `x86_64-w64-mingw32-objcopy`. Integration is indirect through PE build-id/debuglink tests. Risks are that rebuilding with different toolchain versions, alignment options, or build-id implementation changes can invalidate the expected bytes in `pe-file-parsing.c`. Test signal is simply that the generated binary has a discoverable symbol named `main` and matching debug file metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/pe-file.c -->
