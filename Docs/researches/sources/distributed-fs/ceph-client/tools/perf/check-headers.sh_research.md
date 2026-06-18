# sources/distributed-fs/ceph-client/tools/perf/check-headers.sh

### Purpose
`check-headers.sh` validates that perf's vendored copies of kernel UAPI, arch, library, syscall-table, and beauty-generator inputs remain synchronized with their source files in the kernel tree.

### Important APIs, Types, And Functions
Arrays `FILES`, `SYNC_CHECK_FILES`, and `BEAUTY_FILES` enumerate files compared under `tools/`, files compared with sync-ignore regexes, and trace beauty copies under `tools/perf/trace/beauty/`. Functions `check_2()`, `check()`, `beauty_check()`, and `check_ignore_some_hunks()` build diff commands and append failures to `FAILURES`.

### Control Flow
The script first skips cleanly when `../../include` is missing, which handles detached tools tarballs. It changes to the kernel root, runs simple diffs, sync-check diffs, special regex-ignored diffs, non-symmetric syscall-table comparisons, beauty comparisons, duplicated hashmap checks, and finally `check_ignore_some_hunks lib/list_sort.c`. At the end it prints warning lines with `diff -u` commands for every recorded failure.

### State And Persistence
State is shell variables and the `FAILURES` array only. It does not update files; it reports drift.

### Dependencies And Integration Points
It assumes execution from `tools/perf`, access to the kernel source two levels up, GNU-ish `diff`, `grep`, `wc`, Bash arrays, and the ignore-hunk tree under `tools/perf/check-header_ignore_hunks`.

### Risks
The script uses `eval` to run assembled diff commands, so quoted arguments must remain controlled by static arrays. Regex ignore rules can mask unintended changes if too broad. Missing source files are skipped by `check_2()` if the original does not exist, so tree layout changes can reduce coverage.

### Test Signals
Run in a full kernel checkout and in a detached tools-only tree. Expected signals are zero warnings for synced trees, warning commands for deliberately modified copies, and correct skip behavior without `../../include`.
