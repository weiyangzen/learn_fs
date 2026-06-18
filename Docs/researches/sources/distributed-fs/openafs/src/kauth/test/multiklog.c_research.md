## sources/distributed-fs/openafs/src/kauth/test/multiklog.c

Purpose: `multiklog.c` is a klog-derived stress test that repeats AFS authentication a configurable number of times. It is meant to expose repeated-login failures, leaks, and token/ticket behavior rather than serve as a user tool.

Important APIs and control flow: `main` defines a `cmd` syntax with principal, password, tmp ticket file, cell, explicit servers, stdin password, silent mode, lifetime, and `-repeat`. `CommandProc` scrubs command-line arguments, initializes KA, resolves cell/realm, parses server lists, resolves principal from arguments or Unix uid, reads password, converts lifetime strings, applies explicit ubik server lists, and loops `reps` times calling `ka_UserAuthenticateGeneral(KA_USERAUTH_VERSION, ...)`. It records the last non-zero error, zeroes the password buffer, and optionally calls `krb_write_ticket_file` when `-tmp` is set.

State and persistence: repeated authentication updates local token cache state through lower-level auth APIs. Optional `-tmp` writes a Kerberos ticket file. It scrubs command-line password storage and stack password buffer before exit.

Dependencies and integration points: depends on command parser, Unix password database, ubik server parsing, cellconfig, KA authentication APIs, `krb_tf.c` for ticket file writing, and a stub `osi_audit`.

Risks: still uses older C idioms and `strncpy` patterns that may not always terminate. Exit code is the raw KA code in some paths. Repeated authentication can alter the caller's token state unless isolated in a PAG/test environment.

Test signals: default kauth test build target creates `multiklog`, and its primary signal is successful repeated authentication with `-repeat` under real cell credentials.
