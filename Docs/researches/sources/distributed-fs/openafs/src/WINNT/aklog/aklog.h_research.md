# sources/distributed-fs/openafs/src/WINNT/aklog/aklog.h

Purpose: provides the public embedding interface and portability declarations for the aklog implementation.

Important APIs/types: `aklog_params` contains function pointers for filesystem, credential, output, and exit hooks, allowing an embeddable `aklog(int, char **, aklog_params *)` API in older builds. `aklog_init_params` initializes that hook table. It also defines `ARGS` for pre-ANSI compatibility and includes Kerberos/linked-list compatibility headers.

State and dependencies: includes AFS/Kerberos headers and `linked_list.h`; no runtime state is stored in the header. The current `aklog.c` in this subset implements a standalone `main` rather than visibly using the hook table.

Risks and test signals: stale public declarations can diverge from the implementation. Tests or build checks should verify whether embeddable `aklog` symbols are still provided elsewhere or should be reconciled with the standalone Windows command.
