## sources/distributed-fs/openafs/src/kauth/manyklog.c

Purpose: `manyklog.c` is a klog-like stress utility intended to authenticate multiple names in one invocation. It borrows the normal klog command-line shape and adds a `-names` list for repeated `ka_UserAuthenticateGeneral` calls.

Important APIs and control flow: `main` builds a `cmd` syntax with switches for principal, password, tmp ticket file, cell, explicit servers, pipe input, silent mode, lifetime, setpag, and multiple names. `CommandProc` scrubs command-line arguments, initializes KA state with `ka_Init`, resolves the local cell and realm, parses explicit cell/server options, gets the password from the argument, stdin, or `ka_UserReadPassword`, optionally configures ubik server addresses with `ka_ExplicitCell`, and loops over `-names`, calling `ka_UserAuthenticateGeneral` with `KA_USERAUTH_DOSETPAG2` if requested.

State and persistence: stores password in a stack buffer and clears password argument strings. Authentication writes tokens through lower-level KA/KTC helpers. `-tmp` is parsed into `writeTicketFile`, but this source does not actually call `krb_write_ticket_file` after authentication, unlike `multiklog.c`.

Dependencies and integration points: depends on `cmd`, cellconfig, ubik client-list parsing, KA user-auth APIs, Rx shutdown, and Unix user lookup. It also supplies a stub `osi_audit` for linking outside the full audit environment.

Risks: this file appears historically stale or not built by the shown test Makefile. It contains apparent compile issues in the checked source, including `p if (code || !(lcell = ka_LocalCell()))` and use of `itp` without a visible declaration. It should be treated as legacy or broken until a target build proves otherwise. Password handling uses `strncpy` without guaranteed final NUL in several buffers.

Test signals: no build target in `kauth/test/Makefile.in` references `manyklog.c`. Similar maintained behavior is covered by `test/multiklog.c`, which is explicitly the only known-working C test target in that Makefile.
