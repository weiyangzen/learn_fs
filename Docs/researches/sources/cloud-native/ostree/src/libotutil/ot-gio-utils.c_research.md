# sources/cloud-native/ostree/src/libotutil/ot-gio-utils.c

## Purpose
Provides small GIO convenience helpers for path resolution, fsyncing file replacement, unlink-ignore-missing, portable enumerator iteration, cached `GFile` paths, and human-readable duration formatting.

## Important APIs, Types, And Functions
Functions include `ot_gfile_resolve_path_printf`, `ot_gfile_replace_contents_fsync`, `ot_gfile_ensure_unlinked`, compatibility `ot_file_enumerator_iterate` for older GLib, `ot_file_get_path_cached`, and `ot_format_human_duration`.

## Control Flow
Path resolution formats a relative path and resolves it against a `GFile`. Replace uses `glnx_file_replace_contents_at` with datasync. Ensure-unlinked calls `unlink` and ignores `ENOENT`. The old-GLib enumerator implementation fetches the next file and caches info/child via object qdata. Path caching uses a static quark and a global lock to memoize `g_file_get_path`. Duration formatting chooses ns, ms, or seconds based on thresholds.

## State And Persistence Behavior
Persistent writes happen through fsyncing replacement and unlink helpers. Path caching stores qdata on `GFile` objects, and the cache is protected by a static lock.

## Dependencies And Integration Points
Depends on GIO, Unix input/output stream includes, libglnx, and GLib version checks. It supports legacy code paths and common file operations across libostree.

## Risks
`ot_file_get_path_cached` returns `NULL` for non-native `GFile`s, so callers must not assume all `GFile`s have paths. Cached paths reflect the object path, not filesystem renames. Duration formatting names a variable `ms` but divides nanoseconds by 1000, which is actually microseconds; tests may expose misleading labels.

## Test Signals
Tests should cover datasync replacement, unlink missing/existing files, cached path behavior and non-native files, enumerator compatibility where applicable, and duration thresholds.
