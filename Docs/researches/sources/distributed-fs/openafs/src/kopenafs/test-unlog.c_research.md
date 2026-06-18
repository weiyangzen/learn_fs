## sources/distributed-fs/openafs/src/kopenafs/test-unlog.c

Purpose: `test-unlog.c` is a runtime smoke test for clearing tokens via `libkopenafs`.

Important control flow: it checks `k_hasafs`, calls `k_unlog` if available, and prints status plus `errno`; otherwise it reports that AFS is not running.

State and persistence: clears tokens in the current PAG/session through `VIOCUNLOG`.

Dependencies and integration points: includes `kopenafs.h` and standard error/stdio headers. It is built by the kopenafs makefile test target.

Risks: like `test-setpag`, it prints `errno` even on success where it may be stale. `main` does not return an explicit status in the source.

Test signals: expected success is `k_unlog` status 0 on a machine with a native AFS client.
