
# sources/distributed-fs/ceph-client/tools/perf/util/path.c

Purpose: provides small filesystem path helpers for perf utilities.

Important APIs/types/functions: `mkpath` formats into a caller buffer with `vsnprintf`, substitutes `"/bad-path/"` on truncation, and strips leading `./` through `cleanup_path`. `path__join` and `path__join3` concatenate path components with separators. `is_regular_file`, `is_directory`, and `is_directory_at` use `stat`/`fstatat` to test file types.

Control flow: formatting helpers are direct string operations. Directory helpers build or receive paths, stat them, return false on errors, and test mode bits.

State and persistence: no stored state. All outputs are caller buffers or boolean results from current filesystem state.

Dependencies: perf cache/kernel helpers for `scnprintf`, libc stdio/string/stat/dirent/unistd, and `PATH_MAX`.

Integration points: used by PMU/sysfs/file discovery code that needs safe joins and file-type checks, including filesystems where `dirent.d_type` may be `DT_UNKNOWN`.

Risks: `mkpath` is not declared in `path.h` in this slice, so callers may get it through another header. `path__join` does not normalize duplicate separators except empty first path. `strncpy` on truncation may not NUL-fill if size is unusual. Test signals include join edge cases, truncation behavior, DT_UNKNOWN directory scanning, and `fstatat` relative directory checks.
