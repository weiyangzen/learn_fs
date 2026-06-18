<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/klp-build -->
# sources/distributed-fs/ceph-client/scripts/livepatch/klp-build

## Purpose

`klp-build` builds a livepatch kernel module from one or more patch files. It validates livepatch-capable kernel configuration, builds original and patched kernels with function/data sections and objtool checksums, diffs changed objects with `objtool klp diff`, and links the resulting objects into a normal loadable module.

## Important APIs, Types, and Functions

The script is Bash 4.4+ and uses functions as its API: `process_args()`, `validate_config()`, `set_kernelversion()`, patch parsers, `apply_patch()`/`revert_patch()`, `fix_patches()`, `build_kernel()`, `find_objects()`, object copy/diff helpers, `diff_checksums()`, and `build_patch_module()`. Global state includes `PATCHES`, `APPLIED_PATCHES`, `STASHED_FILES`, temp subdirectories, `NAME`, `OUTFILE`, `REPLACE`, `SHORT_CIRCUIT`, `JOBS`, and debug/verbosity flags.

## Control Flow

The main path processes arguments, initializes temp state, validates patches, builds a clean original tree, copies original `.o` files for `vmlinux.o` and modules, fixes patch line numbers with `fix-patch-lines` and `recountdiff`, applies patches, builds the patched tree, copies changed objects, diffs them through objtool, optionally identifies first changed instructions, and builds a final module under `klp-tmp/kmod`. Short-circuit mode resumes at selected stages when a preserved temp tree exists.

## State and Persistence Behavior

Persistent effects are intentionally bounded but invasive during execution: it applies and reverts source patches, temporarily modifies `scripts/setlocalversion`, runs kernel builds, creates `klp-tmp`, writes logs and copied object trees, and emits the final `.ko`. Cleanup traps revert patches, restore stashed files, and remove temp state unless `--keep-tmp`, debug, or short-circuit behavior requests preservation.

## Dependencies and Integration Points

It integrates with top-level Kbuild, `.config`, `scripts/livepatch/init.c`, `tools/objtool/objtool`, GNU `patch`, `gawk`, `find`, `objcopy`, `recountdiff` from patchutils, and `fix-patch-lines`. It depends on `CONFIG_LIVEPATCH`, `CONFIG_KLP_BUILD`, compatible objtool support, and unsupported-patch filters for `lib/*` and assembly.

## Risks and Edge Cases

The script mutates a live source tree and relies on trap cleanup, so interrupted or externally modified runs can leave patched files or temp output. It rejects some unsupported inputs but cannot prove semantic livepatch safety. Timestamp-based changed-object discovery is backed by `cmp`, but stale objects and unusual out-of-tree layouts are explicitly unsupported. Missing objtool, bad `.cmd` data, modpost warnings, BTF corruption, or kernel config plugins can fail late.

## Test Signals

Good signals are dry-run patch validation, clean original and patched build logs, non-empty diff objects, successful `objtool klp post-link`, a final loadable `.ko`, and `--show-first-changed` output for known function edits. Regression tests should cover fuzzed patches, multiple patches, `--no-replace`, short-circuit resume, unsupported paths, missing config flags, and cleanup after failed builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/livepatch/klp-build -->
