# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-stat.c

## Purpose

`metadisp-stat.c` returns authoritative stat data for split metadata/data objects and supports calls initiated by lower metadata layers that request a specific stat source.

## Important APIs, Types, and Functions

Functions are `metadisp_stat`, `metadisp_stat_cbk`, `metadisp_stat_resume`, and `metadisp_stat_backend_cbk`.

## Control Flow

`metadisp_stat` first filters root by winding directly to metadata. If xdata contains `syncop-internal-from-posix` and `stat-source-of-truth`, it treats the call as metadata-layer internal and winds to the data child using the supplied source xlator context. Otherwise it builds a backend loc, creates a stat resume stub, and winds stat to `METADATA_CHILD`. The metadata callback unwinds immediately for non-regular objects or errors, and resumes the backend stat for regular files. Backend `ENOENT` is converted to `ENODATA`, while null GFID produces `EUCLEAN`.

## State and Persistence Behavior

No internal state persists. The fop reconciles persistent stat data between metadata and data children and may signal corruption or missing data through `EUCLEAN` or `ENODATA`.

## Dependencies and Integration Points

The file integrates with `METADISP_FILTER_ROOT`, `build_backend_loc`, xdata keys `syncop-internal-from-posix` and `stat-source-of-truth`, and the readdir path that sets the stat source hint.

## Risks and Edge Cases

The code uses `STACK_UNWIND_STRICT(open, ...)` in some stat error paths, which appears inconsistent with a stat fop and is a compile/runtime risk depending on macro signatures. Missing data after metadata success requires healing behavior outside this file. Internal-from-posix handling depends on raw pointer xdata and must only be used within the process.

## Test Signals

Tests should cover root stat, directory stat, regular file stat through both children, data missing, null GFID, readdirp-triggered stat-source-of-truth, and compile/signature checks around the apparent `open` unwind typo.
