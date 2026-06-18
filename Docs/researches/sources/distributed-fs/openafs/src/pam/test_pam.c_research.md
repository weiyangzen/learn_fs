<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/test_pam.c -->
# sources/distributed-fs/openafs/src/pam/test_pam.c

## Purpose
Provides a standalone interactive test driver for PAM stacks using the `afstest` service. It authenticates a named user, optionally establishes credentials, opens a session, then launches a shell for manual inspection.

## Important APIs, Types, And Functions
The program uses `pam_start`, `pam_authenticate`, `pam_acct_mgmt`, `pam_setcred`, `pam_open_session`, `pam_end`, a custom `my_conv` PAM conversation, `getpass`/`getpassphrase`, `putenv`, `chdir`, and `execl`. Option `-u` disables `pam_setcred`.

## Control Flow
`main` parses `[-u] <user>`, starts PAM for service `afstest`, authenticates, runs account management, optionally establishes credentials, opens a session, ends PAM, sets test environment variables, changes to `/tmp`, and execs `/bin/csh`. `my_conv` handles echo-off password prompts, echo-on input, error messages, and text info by allocating response arrays and reading from terminal/stdin.

## State And Persistence
The program starts a PAM transaction and may create credentials/tokens depending on the configured stack. It sets process environment variables and replaces itself with a shell; it does not write files.

## Dependencies And Integration Points
It is built by `Makefile.in` for PAM module testing and depends on a system PAM service named `afstest`. It exercises the OpenAFS module through the normal PAM API rather than direct calls.

## Risks And Test Signals
Risks include hard-coded `/bin/csh`, use of `getpass`, manual-only behavior, and limited cleanup after opening sessions because it calls `pam_end` before launching the shell rather than testing close-session. Test signals include successful auth/setcred/open-session, expected token visibility inside the shell, `-u` behavior without credentials, and conversation handling for prompt/message styles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/test_pam.c -->
