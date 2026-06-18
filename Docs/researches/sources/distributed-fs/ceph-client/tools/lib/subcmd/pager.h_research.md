# sources/distributed-fs/ceph-client/tools/lib/subcmd/pager.h

Purpose: Public header for libsubcmd pager setup and query APIs.

Important APIs/types/functions: Declares `pager_init()`, `setup_pager()`, `pager_in_use()`, `pager_get_columns()`, and `force_pager()`.

Control flow: Callers initialize the pager environment variable name, optionally force a pager, call `setup_pager()` before output, and query status/columns as needed.

State and persistence: State is implementation-private in `pager.c`.

Dependencies/integration: Guarded by `__SUBCMD_PAGER_H`; installed with libsubcmd headers.

Risks: API does not expose shutdown; cleanup is atexit/signal based. Call ordering matters because `pager_init()` sets the environment variable key used later.

Test signals: Compile against header and verify behavior through `pager.c` integration tests.
