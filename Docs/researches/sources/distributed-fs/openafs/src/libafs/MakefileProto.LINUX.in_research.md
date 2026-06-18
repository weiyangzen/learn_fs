<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.LINUX.in -->
# sources/distributed-fs/openafs/src/libafs/MakefileProto.LINUX.in

## Purpose
Platform-specific kernel-libafs makefile prototype for Linux. It builds Linux libafs and afspag kernel modules, using legacy direct `ld -r` rules for old kernels and Kbuild-generated Makefiles for Linux 2.6+ kernels. The file is processed with OpenAFS' angle-bracket system-name conditionals before becoming the concrete build makefile.

## Important APIs, Types, And Functions
Key make interfaces are `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, compiler/linker flag variables, `KOBJ`, `COMPDIRS`, `INSTDIRS`, `DESTDIRS`, `setup`, `libafs`, `install_libafs`, and `dest_libafs`. Notable platform-specific details include kernel header symlink setup, architecture-specific `asm` links, `make_kbuild_makefile.pl`, `.makelog` warning/failure scanning, packaging-friendly install paths, and `SPARSE_MAKEFLAGS`.

## Control Flow
The generated makefile prepares kernel header symlinks and object directories in `setup`, includes `Makefile.common`, and delegates common object compilation to that shared file. Platform targets then link, archive, install, or skip the selected libafs flavor according to this platform's kernel-module conventions.

## State And Persistence
Persistent output is limited to build/install artifacts such as kernel extension objects, archives, `.ko` files, maps/debug bundles, module metadata, and staged files under `DESTDIR` or `DEST`. Runtime AFS state is not touched; this file only shapes the build tree.

## Dependencies And Integration Points
The template depends on `Makefile.config`, `Makefile.common`, platform kernel headers and toolchains, generated OpenAFS RPC sources, and OS-specific source files under `src/afs/<ostype>`. It is selected by OpenAFS configure/sysname logic and participates in the top-level libafs build.

## Risks And Test Signals
Risks include stale platform flags, missing kernel headers, bitness or architecture mismatches, unsupported NFS-translator assumptions, path/symlink drift, and divergence from `Makefile.common` object names. Useful signals are configure output for this sysname, a clean `make libafs`, install/dest smoke checks, and inspection of module load/link errors on the target OS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/MakefileProto.LINUX.in -->
