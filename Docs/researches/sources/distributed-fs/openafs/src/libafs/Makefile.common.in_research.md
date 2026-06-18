<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/Makefile.common.in -->
# sources/distributed-fs/openafs/src/libafs/Makefile.common.in

## Purpose
Defines common kernel-libafs build inputs shared by all platform `MakefileProto.*.in` templates. It centralizes include paths, generic build rules, common object lists for libafs, NFS-translator, non-NFS, and PAG-manager variants, per-object compile rules, crypto support objects, generated RPC/XDR objects, platform-specific object hooks, and cleanup behavior.

## Important APIs, Types, And Functions
The important make variables are `COMMON_INCLUDE`, `AFSAOBJS`, `AFSNFSOBJS`, `AFSNONFSOBJS`, `AFSPAGOBJS`, `AFS_OS_OBJS`, `AFS_OS_NFSOBJS`, `AFS_OS_NONFSOBJS`, and `AFS_OS_PAGOBJS`. Rules define `CRULE_NOOPT` and `CRULE_OPT` usage for many source files from `afs`, `afs/VNOPS`, `rx`, `rxkad`, `rxstat`, `fsint`, `vlserver`, `sys`, `util`, and Heimdal crypto sources. Targets include `system`, `install`, `dest`, `all`, single-directory wrappers, `depsrcs`, and `clean`.

## Control Flow
Platform makefiles include this file after setting compiler flags, object hooks, module names, and directory targets. `all` runs setup and platform component directories. Single-directory targets enter `$(KOBJ)` and delegate to `_libafs` targets. Object rules compile common code from the source or generated object tree, selectively using optimized or non-optimized rules. Platform-specific object rules are intentionally common here so platform makefiles only select which OS objects are active.

## State And Persistence
The file creates build artifacts in platform object directories and installs no persistent runtime state by itself. It removes generated include symlinks and build directories during `clean`. The object lists persist the build contract for which code is linked into each kernel module flavor.

## Dependencies And Integration Points
It is included by every `MakefileProto` in `src/libafs`. It depends on `Makefile.config`, generated RPC sources under `TOP_OBJDIR`, kernel crypto sources, the rx/rxkad trees, OS-specific `afs/$(MKAFS_OSTYPE)` source directories, and `Makefile.version` for component version generation.

## Risks And Test Signals
Risks include missing source/object mappings, duplicated object names across variants, incorrect optimization selection for fragile kernel code, include-path ordering bugs, and platform makefiles relying on variables defined before inclusion. Test signals are successful kernel-module builds for representative platforms, Linux Kbuild generation, NFS/non-NFS/PAG object coverage, clean rebuilds after `make clean`, and generated RPC dependency freshness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/Makefile.common.in -->
