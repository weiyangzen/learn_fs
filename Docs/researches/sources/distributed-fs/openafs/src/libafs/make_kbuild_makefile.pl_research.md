<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/make_kbuild_makefile.pl -->
# sources/distributed-fs/openafs/src/libafs/make_kbuild_makefile.pl

## Purpose
Generates a Linux 2.6+ Kbuild-compatible Makefile for OpenAFS kernel modules. It scans the already-generated libafs makefiles, resolves object lists and source dependencies, symlinks source files into the kernel build directory, creates compatibility include shims when needed, and writes Kbuild object/CFLAGS assignments for `libafs` and `afspag`.

## Important APIs, Types, And Functions
The command-line contract is `make_kbuild_makefile.pl KDIR TARG Makefiles...`. Important variables parsed from makefiles include `TOP_OBJDIR`, `TOP_SRCDIR`, `AFSAOBJS`, `AFSNFSOBJS`, `AFSPAGOBJS`, `COMMON_INCLUDE`, `CFLAGS`, `LINUX_KERNEL_PATH`, and `LINUX_KBUILD_CFLAGS_VAR`. Internal maps are `%vars`, `%deps`, `%all_objs`, `%remap`, and `%seen`.

## Control Flow
The script reads each makefile line-by-line, joins continuations, ignores comments, substitutes previously-seen `$(VAR)`/`${VAR}` references, stores variable assignments, and records `.o: .c` or `.o: .s` dependencies. It special-cases `AFS_component_version_number.o`, computes target object lists, creates `TOP_OBJDIR/src/libafs/KDIR`, symlinks source files with `.c` or `.S` names, sets up `h`, `netinet`, and `sys` mappings either as Linux header symlinks or generated wrapper directories, recursively scans includes for shim headers on older layouts, and writes the Kbuild Makefile with per-object flags plus `obj-m`, target objects, and `afspag-objs`.

## State And Persistence
Persistent state is the generated Kbuild directory: symlinked sources, include shims, and `Makefile`. Existing generated source links with matching names are unlinked and recreated. The script does not modify the original makefiles or runtime system state.

## Dependencies And Integration Points
It is invoked by `MakefileProto.LINUX.in` before running `make -C LINUX_KERNEL_BUILD M=... modules`. It depends on Perl `IO::File`, OpenAFS makefile variable ordering, kernel header layout, and complete object dependency rules in `Makefile.common`/`Makefile.afs`.

## Risks And Test Signals
Risks include simplistic makefile parsing, variables used before assignment, one-dependency assumptions, shell conditionals not represented in the parsed text, stale symlinks, crude recursive deletion for remap directories, and missing/unrecognized include syntax. Useful signals are a generated `Makefile` with all expected object lists, no `No source known` failures, successful `libafs.ko` and `afspag.ko` Kbuild builds, and warning-free `.makelog` scanning by the Linux proto makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/make_kbuild_makefile.pl -->
