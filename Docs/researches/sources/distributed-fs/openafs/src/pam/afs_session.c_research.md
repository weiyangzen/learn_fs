<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_session.c -->
# sources/distributed-fs/openafs/src/pam/afs_session.c

## Purpose
Implements PAM session hooks for OpenAFS token cleanup. Opening a session is a no-op; closing a session optionally destroys tokens immediately or after a delay.

## Important APIs, Types, And Functions
Exports `pam_sm_open_session` and `pam_sm_close_session`. Close-session options are `debug`, `remain`, `remainlifetime <seconds>`, and `no_unlog`. It uses `fork`, `setsid`, `sleep`, `ktc_ForgetAllTokens`, syslog, and `pam_afs_syslog`.

## Control Flow
`pam_sm_open_session` returns success. `pam_sm_close_session` parses options, and if `remain` is set without `no_unlog`, forks a detached child that closes file descriptors, sleeps for the configured lifetime, then forgets tokens; the parent logs session closed and returns success. Without delayed cleanup, it calls `ktc_ForgetAllTokens` immediately unless `no_unlog` is set.

## State And Persistence
The only persistent effect is deletion of AFS tokens from the current PAG/token context. Delayed cleanup creates a short-lived child process with no retained PAM state.

## Dependencies And Integration Points
This hook complements auth/setcred token establishment and is included in `pam_afs` exports. It relies on OpenAFS token cache semantics and syslog.

## Risks And Test Signals
Risks include token cleanup affecting shared PAGs, delayed child process behavior during logout, weak parsing of missing `remainlifetime` argument, and closing only descriptors 0-63. Test signals include immediate and delayed `unlog` behavior, `no_unlog`, invalid lifetime handling, and session close under Linux and non-Linux process-group semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_session.c -->
