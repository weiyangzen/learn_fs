# sources/distributed-fs/openafs/src/config/make_libafs_tree.pl

Purpose: Perl utility that constructs a standalone `libafs_tree` by copying source/object files listed in `libafsdep` dependency manifests.

Important APIs/types/functions: parses `-t`, `-p`, `-o`, `-sn`, `-os`, `-q`, and `-n`; uses `File::Find` to locate `libafsdep`; `process_libafsdep` expands manifest entries and `MKAFS_OSTYPE`; `mkfullpath` recreates source-relative directories; `copyit` copies files with `cp -p` when size or mtime differ.

Control flow: validates required project directory, tree directory, sysname, and ostype, scans the source tree for dependency manifests, copies each listed source/object file or glob, manually copies `configure-libafs`, `Makefile-libafs.in`, and the OS-specific `src/libafs/MakefileProto`, writes `.version` via `build-tools/git-version` unless dry-run, and removes generated `include/afs/param.h` so the target tree regenerates it.

State and persistence: creates or updates the libafs tree directory and its copied files. Dry-run mode prints actions without copying.

Dependencies and integration: used by libafs packaging/build workflows; depends on Perl core modules, `cp`, OpenAFS `libafsdep` manifests, build-tools git versioning, and source/object directory layout.

Risks and test signals: risks include commented-out tree cleanup leaving stale files, glob overreach, path quoting in printed/system commands, and copy freshness based only on size/mtime. Signals are dry-run output, complete libafs tree generation, regenerated `param.h`, and successful standalone libafs build from the tree.
