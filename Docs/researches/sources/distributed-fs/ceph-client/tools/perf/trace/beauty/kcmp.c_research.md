# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kcmp.c

Purpose: This formatter supports `kcmp(2)` argument rendering, especially the `type`, `idx1`, and `idx2` relationship.

Important APIs/types/functions: `syscall_arg__scnprintf_kcmp_type` maps `KCMP_*` values using the generated `kcmp_type_array.c`; `syscall_arg__scnprintf_kcmp_idx` formats file indexes as process file descriptors when type is `KCMP_FILE`; `kcmp__scnprintf_type` wraps the shared `strarray` lookup.

Control flow: The type formatter checks the selected comparison type and masks out `idx1`/`idx2` for all non-file comparisons because those arguments are ignored by the kernel. The index formatter reads syscall argument 2 for the type and falls back to numeric output unless it is `KCMP_FILE`; for file comparisons it chooses pid1 or pid2 based on the current argument index and calls `pid__scnprintf_fd`.

State and persistence: It mutates only `arg->mask` for display suppression. No data is persisted.

Dependencies and integration points: It depends on `uapi/linux/kcmp.h`, `machine.h`, generated type arrays, and perf thread/file descriptor lookup helpers.

Risks: Incorrect argument indexes would associate an fd with the wrong process. New `KCMP_*` values require regenerated arrays.

Test signals: Trace `kcmp` with `KCMP_FILE` and a non-file type. Verify fd arguments are named for file comparisons and hidden for non-file comparisons.
