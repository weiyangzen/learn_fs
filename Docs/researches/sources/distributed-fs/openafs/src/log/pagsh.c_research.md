## sources/distributed-fs/openafs/src/log/pagsh.c

Purpose: Starts a shell in a new AFS PAG, optionally also creating a new Kerberos token PAG in Kerberos builds.

Important APIs and functions: `main` uses `getuid`, `getpwuid`, `setpag`, optional `ktc_newpag`, and `execvp`.

Control flow: On AIX it installs full-dump signal actions for better core files. It determines the current uid and passwd entry, but the code leaves shell as hard-coded `/bin/sh` rather than using `pw_shell`. It calls `setpag` and reports errors, calls `ktc_newpag` in `AFS_KERBEROS_ENV`, then replaces the process image with the shell while preserving argument vector after rewriting `argv[0]`.

State and persistence: Mutates the process credential/PAG state before exec. No files are written.

Dependencies and integration: Built as `pagsh` and `pagsh.krb` by `src/log/Makefile.in`. Depends on AFS auth/sys prototypes and RX headers.

Risks: Shell selection ignores the user's passwd shell. If `setpag` fails, the program still execs a shell, which may surprise callers expecting failure. `argv` is passed through to `/bin/sh`, so pagsh arguments become shell arguments.

Test signals: Run and inspect PAG change, failure behavior when `setpag` is unavailable, Kerberos build invoking `ktc_newpag`, AIX signal setup compilation, and exec argument handling.
