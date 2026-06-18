<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_auth.c -->
# sources/distributed-fs/openafs/src/pam/afs_auth.c

## Purpose
Implements `pam_sm_authenticate` for legacy AFS/KA authentication. It validates an AFS password, optionally obtains tokens during authentication for applications that do not call `pam_setcred`, creates PAGs, supports `klog` fallback, and stores the password in PAM data for later credential establishment.

## Important APIs, Types, And Functions
The function uses PAM APIs (`pam_get_user`, `pam_get_item`, `pam_set_item`, `pam_set_data`), OpenAFS calls (`setpag`, `ktc_newpag`, `ktc_ForgetAllTokens`, `ka_VerifyUserPassword`, `ka_UserAuthenticateGeneral`), helper calls (`pam_afs_prompt`, `pam_afs_syslog`, `do_klog`, `lc_cleanup`), and platform-specific `getpwnam`/`getpwnam_r`. Options include `debug`, `nowarn`, `use_first_pass`, `try_first_pass`, `ignore_root`, `ignore_uid <n>`, `cell <name>`, `refresh_token`, `set_token`, `dont_fork`, `use_klog`, and accepted `setenv_password_expires`.

## Control Flow
The hook parses options, gets a PAM conversation and user, optionally ignores low-UID users, retrieves `PAM_AUTHTOK` or prompts for a password, rejects empty passwords, creates a PAG unless refreshing, and authenticates. By default it forks so KA library state/sockets are cleaned up in the child; `dont_fork` authenticates inline, while `use_klog` runs the external `klog`/`klog.krb` helper. If `try_first_pass` fails it reprompts. On success it returns `PAM_SUCCESS`; `KANOENT` maps to `PAM_USER_UNKNOWN`; other failures map to `PAM_AUTH_ERR`.

## State And Persistence
The module stores a duplicate password under `pam_afs_lh` with cleanup that zeros it on PAM end, may set `PAM_AUTHTOK`, creates a PAG in the process, and may obtain AFS tokens when `refresh_token` or `set_token` is used. Prompted passwords are copied into fixed 256-byte stack buffers and wiped before exit when owned.

## Dependencies And Integration Points
It is the authentication half of `pam_afs.so`/`pam_afs.krb.so` and feeds `afs_setcred.c` through PAM data. It integrates with KA servers, optional Kerberos-klog behavior, syslog, PAM conversation callbacks, and platform NSS.

## Risks And Test Signals
Risks include legacy KA security, fixed-size password buffer truncation, broad use of syslog around auth failures, fork/signal-handler interactions, retained password material in PAM data, and option conflict handling. Test signals include `use_first_pass`/`try_first_pass`/prompt flows, ignored UID behavior, alternate cell auth, token/PAG creation, `dont_fork` and `use_klog` modes, `KANOENT` user mapping, and password cleanup under `pam_end`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_auth.c -->
